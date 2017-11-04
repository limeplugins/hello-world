import http.client
import json
import lime_test.core_db.dsl as dsl
import lime_test.app
import lime_test.db
import lime_test.web_app
import lime_type
import pytest


@pytest.fixture
def limetypes():
    """The limetypes of the core database

    You can change these, or create your own by twiddling with the YAML based
    DSL format for limetypes.
    """
    return lime_type.create_limetypes_from_dsl(dsl.dsl)


@pytest.fixture
def database(limetypes, monkeypatch):
    """An in-memory empty Lime database with the core database limetypes"""
    database = lime_test.db.create_database_with_limetypes(monkeypatch,
                                                           limetypes=limetypes,
                                                           limename='myapp',
                                                           sqlname='myapp')
    return database


@pytest.fixture
def limeapp(database, limetypes, monkeypatch):
    """A Lime application with a user/coworker defined"""
    app = lime_test.app.create_app(monkeypatch, database, limetypes)
    user = lime_test.db.create_and_add_user(database=database,
                                            fullname='Kenny Starfighter',
                                            username='kenny',
                                            password='kenny')
    app.unit_of_work()

    # TODO: Make it possible to create a coworker with this hack
    coworker = app.limetypes.coworker(
        firstname='Kenny',
        lastname='Starfighter',
        name='Kenny Starfighter',
        username=user.id,
        _from_row=True
    )

    uow = app.unit_of_work()
    idx = uow.add(coworker)
    res = uow.commit()

    app._coworker = res.get(idx)

    return app


@pytest.fixture
def webapp(limeapp, database, monkeypatch):
    """An in-memory web application where you're authenticated as a user"""
    web_app = lime_test.web_app.create_web_app(database, monkeypatch)

    return lime_test.web_app.create_authenticated_web_client(web_app=web_app,
                                                             app=limeapp,
                                                             username='kenny',
                                                             password='kenny')


@pytest.fixture
def acme_company(limeapp):
    """A company that gets added to `limeapp`"""
    uow = limeapp.unit_of_work()
    acme = limeapp.limetypes.company(name='Acme Inc.')
    acme_idx = uow.add(acme)
    res = uow.commit()
    return res.get(acme_idx)


def test_add_a_deal_returns_its_id(webapp, acme_company):

    payload = {
        'name': 'A new deal',
        'value': 123000,
        'probability': 90,
        'company_id': acme_company.id,
    }

    res = webapp.post('/myapp/hello-world/deal/',
                      data=json.dumps(payload),
                      headers={'Content-Type': 'application/json'})

    assert res.status_code == http.client.CREATED

    json_response = json.loads(res.data.decode('utf-8'))

    assert json_response == {
        'deal_id': 1
    }


def test_add_a_deal_saves_to_the_database(webapp, limeapp, acme_company):
    payload = {
        'name': 'A new deal',
        'value': 123000,
        'probability': 90,
        'company_id': acme_company.id,
    }

    res = webapp.post('/myapp/hello-world/deal/',
                      data=json.dumps(payload),
                      headers={'Content-Type': 'application/json'})

    json_response = json.loads(res.data.decode('utf-8'))

    deal = limeapp.limetypes.deal.get(json_response['deal_id'])

    assert deal.properties.name.value == 'A new deal'

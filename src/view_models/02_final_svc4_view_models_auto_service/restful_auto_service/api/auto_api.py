from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from restful_auto_service.data.car import Car
from restful_auto_service.data.repository import Repository
from restful_auto_service.viewmodels.create_auto_viewmodel import CreateAutoViewModel


@view_config(route_name='autos_api',
             request_method='GET',
             renderer='negotiate')
def all_autos(_):
    cars = Repository.all_cars(limit=25)
    return cars


@view_config(route_name='auto_api',
             request_method='GET',
             renderer='negotiate')
def single_auto(request: Request):
    car_id = request.matchdict.get('car_id')
    if car_id == '__first__':
        car_id = Repository.all_cars()[0].id

    car = Repository.car_by_id(car_id)
    if not car:
        msg = "The car with id '{}' was not found.".format(car_id)
        return Response(status=404, json_body={'error': msg})

    return car


@view_config(route_name='autos_api',
             request_method='POST',
             renderer='json')
def create_auto(request: Request):
    try:
        car_data = request.json_body
    except Exception as x:
        return Response(status=400, body='Could not parse your post as JSON.' + str(x))

    vm = CreateAutoViewModel(car_data)
    vm.compute_details()
    if vm.errors:
        return Response(status=400, body=vm.error_msg)

    try:
        car = Repository.add_car(vm.car)
        return Response(status=201, json_body=car.to_dict())
    except Exception as x:
        return Response(status=500, body='Could not save car. ' + str(x))


# noinspection PyBroadException
@view_config(route_name='auto_api',
             request_method='PUT')
def update_auto(request: Request):
    car_id = request.matchdict.get('car_id')
    car = Repository.car_by_id(car_id)
    if car_id == '__first__':
        car_id = Repository.all_cars()[0].id

    if not car:
        msg = "The car with id '{}' was not found.".format(car_id)
        return Response(status=404, json_body={'error': msg})

    try:
        car_data = request.json_body
        car = Car.from_dict(car_data)
    except:
        return Response(status=400, body='Could not parse your post as JSON.')

    # TODO: Validate

    try:
        Repository.update_car(car)
        return Response(status=204, body='Car updated successfully.')
    except:
        return Response(status=400, body='Could not update car.')


# noinspection PyBroadException
@view_config(route_name='auto_api',
             request_method='DELETE')
def delete_auto(request: Request):
    car_id = request.matchdict.get('car_id')
    car = Repository.car_by_id(car_id)
    if not car:
        msg = "The car with id '{}' was not found.".format(car_id)
        return Response(status=404, json_body={'error': msg})

    try:
        Repository.delete_car(car_id)
        return Response(status=204, body='Car deleted successfully.')
    except:
        return Response(status=400, body='Could not update car.')

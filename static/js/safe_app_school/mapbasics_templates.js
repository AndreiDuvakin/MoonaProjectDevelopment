function init() {
    // Задаём точки мультимаршрута.
    var pointA = <point1>,
        pointB = <point2>,
        /**
         * Создаем мультимаршрут.
         * @see https://api.yandex.ru/maps/doc/jsapi/2.1/ref/reference/multiRouter.MultiRoute.xml
         */
        multiRoute = new ymaps.multiRouter.MultiRoute({
            referencePoints: [
                pointA,
                pointB
            ],
            params: {
                //Тип маршрутизации - пешеходная маршрутизация.
//                routingMode: 'pedestrian'
            }
        }, {
            // Автоматически устанавливать границы карты так, чтобы маршрут был виден целиком.
            boundsAutoApply: true
        });

    // Создаем карту с добавленной на нее кнопкой.
    var geolocation = ymaps.geolocation, myMap = new ymaps.Map('map', {
        center: [55.739625, 37.54120],
        zoom: 12
    });

    geolocation.get({
        provider: 'browser',
        mapStateAutoApply: true
    }).then(function (result) {
        // Синим цветом пометим положение, полученное через браузер.
        // Если браузер не поддерживает эту функциональность, метка не будет добавлена на карту.
        result.geoObjects.options.set('preset', 'islands#redCircleIcon');
        myMap.geoObjects.add(result.geoObjects);
    });

    // Добавляем мультимаршрут на карту.
    myMap.geoObjects.add(multiRoute);
}
ymaps.ready(init);
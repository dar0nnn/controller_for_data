# controller_for_data

Данный репозиторий содержит в себе функционал контроллера, который должен обеспечивать сохранение данных в системе при изменении количества контроллеров и других внештаных ситуациях.
Если кратко: контроллер - это интеллектуальный агент, созданный для мультиагентной системы.

ScalesActionLocal: локальные действия агента
Behavior: действия, выполняемые по сети
db_api: модуль взаимодействия с базой
ServerAPI: нужен для инициализации API сервера, для взаимодействия с внешними системами

Некоторые импорты удалены из за NDA
Так же удален модуль, отвечающий за инициализацию сервера Агента и файл конфига.

Данный контроллер написан для использования в системах, сертефицированных ФСТЭК.

Версия Python: 2.7.14
Версия PostgreSQL: 9.3
Написан для операционной системы Linux Astra 1.5 Smolensk
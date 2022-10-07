# Astra Linux mininet container

### Описание

Использование дистрибутива Astra Linux (Orel) в качестве основы для Docker контейнера на стенде mininet. Ноды с Astra Linux в mininet демонстрационного стенда используются в качестве маршрутизаторов с протоколами OSPF и RIP (на основе пакета FRR).

Инструкция может быть применена на хост-машине под управлением Ubuntu подобной ОС.

### Файлы

Необходимые файлы для работы:

```
build-docker-image.sh (для сборки контейнера Astra Linux)
example.py (для запуска стенда mininet)
```

### Сборка образа Astra Linux

#### Установка необходимых пакетов

```
sudo apt-get update
sudo apt-get install -y docker.io debootstrap
```

#### Добавление текущего пользователя в группу docker

```
sudo usermod -aG docker $USER
```

После этого нужно перелогиниться в систему.

#### Создание ссылки на скрипт для сборки редакции Orel

```
sudo ln -s /usr/share/debootstrap/scripts/sid /usr/share/debootstrap/scripts/orel
```

#### Сборка образа

```
./build-docker-image.sh
```

В результате работы скрипта будет создан образ astra_linux_ce-frr:2.12, содержащий Astra Linux и пакет FRR.

### Запуск mininet

Контейнеры Docker запускаются при помощи containernet (форк minint).

#### Скачивание образа containernet

```
docker pull containernet/containernet
```

#### Запуск образа containernet

```
docker run --name containernet -it --rm --privileged --pid='host' \
   -v /var/run/docker.sock:/var/run/docker.sock \
   -v $(pwd):/host \
   containernet/containernet \
   python3 /host/example.py
```

Будет создан стенд с тремя Astra Linux маршрутизаторами FRR и тремя хостами подключенными к ним.

![](lab.png)

# P.S.

Это наш первый сайт, который мы делали, когда мы учились в Яндекс Лицее.

# K8S

Для приложения были разработаны манифесты K8S, ключ шифрования был вынесен в секреты, [пример секрета](k8s/helm/moona/templates/examples_secrets.yaml).  
Чтобы запустить приложение необходимо проделать несколько шагов:

### Шаг 1: Подготовка кластера Kubernetes

- Убедись, что кластер работает (у меня, MicroK8s).
- Установи Helm:
    ```bash
    curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
    ```
### Шаг 2: Подготовка Helm-чарта

- Проверь файлы: `Chart.yaml`, `values.yaml`, папка `templates`.
### Шаг 3: Создание секрета

- Создай секрет `moona-secret`:
    ```bash
    kubectl create secret generic moona-secret --from-literal=SECRET_KEY='мой-секретный-ключ'
    ```
    или через манифест:
	```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: moona-secret
    type: Opaque
    data:
      SECRET_KEY: your_secret_key
    ```
 
### Шаг 4: Развертывание приложения через Helm
- Установи чарт:
    ```bash
    cd путь/к/чарту
    helm install moona-app . --namespace moona --create-namespace
    ```
### Шаг 5: Проверка развертывания
- Проверь поды:    
    ```bash
    kubectl get pods -n moona
    ```    
- Проверь сервисы:
```bash
kubectl get services -n moona
```
- Проверь Ingress: 
```bash
kubectl get ingress -n moona
```
- Проверь сертификат: 
```bash
kubectl get certificates -n moona
```

### Шаг 6: Доступ к приложению

- Адрес: `https://moona.numerum.team/`.
- Настрой DNS для `moona.numerum.team`.
### Дополнительно
- Обновление:
```bash
helm upgrade moona-app . --namespace moona
```
- Удаление:
```bash
helm uninstall moona-app -n moona
```

# MOONA

![string_moona.png](moona/static/img/string_moona.png)
**moona** – это сайт-дневник, который позволяет поделится своими мыслями с другими пользователями. На сайте после
регистрации, можно добавлять записи в свой личный дневник и при желании делать запись доступной для всех пользователей
сайта.

Moona выполнена в светло-голубых тонах, чтобы пользователей ничего не отвлекало от использования нашего сайта. На нашем
сайте каждый сможет найти что-то подходящее для себя: каждый в праве писать посты для всех или только для себя.

Чуть позже здесь появятся картинки нашего сайта с окончательным дизайном, нужно лишь чуть чуть подождать

Посмотреть наш сайт вы можете перейдя по ссылке https://moona.net.ru/diary/
____

# Контактики

### Email:

- andrei@duvakin.ru
- tolmenevadarya@yandex.ru
- moonadiary@yandex.ru (оффициальная почта)

### VK:

- https://vk.com/andreiduvakin
- https://vk.com/s_plombir19

### Telegram:

- @andrei_duvakin
- @DinPg

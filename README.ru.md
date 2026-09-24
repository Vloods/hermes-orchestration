# Hermes Orchestration — руководство

[English README](README.md) · [Архитектура](docs/architecture.md) · [Безопасность](docs/security.md)

Это независимый стартовый набор конфигурации для Hermes Agent, **не официальный проект Nous Research**. Основной профиль (`astra`, low) принимает решения, ограниченные дочерние задачи выполняются на `sol`, medium (не более трёх одновременно, глубина 1), а долговременные задачи передаются через Kanban назначенным профилям. Отдельный `solver` (`sol`, high) нужен для сложной проверки; он не вызывается автоматически. Десять вспомогательных ролей используют `luna`, low. Идентификаторы моделей — снимок одной установки, не гарантированные имена или права доступа: замените провайдера и модели параметрами скрипта. Шаблон не закрепляет `model.api_mode`; установленный Hermes выбирает протокол для заданного провайдера/модели, проверьте его после замены. Скорость, экономия и стоимость не измерялись.

## Запуск с нуля

1. Установите Hermes по [официальной инструкции](https://hermes-agent.nousresearch.com/docs/getting-started/installation), проверьте `hermes --version`. Авторизация — только через официальный `hermes setup` для выбранного `HERMES_HOME`; ключей в репозитории нет.
2. Склонируйте `https://github.com/Vloods/hermes-orchestration.git`, перейдите в каталог `hermes-orchestration` и выберите **новый абсолютный** путь для изолированного дома Hermes:

   ```bash
   SANDBOX="$(mktemp -d)/hermes-home"
   python3 scripts/render.py --home "$SANDBOX"           # только предпросмотр
   python3 scripts/render.py --home "$SANDBOX" --apply   # записать шаблоны
   HERMES_HOME="$SANDBOX" hermes setup
   HERMES_HOME="$SANDBOX" hermes profile list
   ```

   При другом провайдере задайте `--provider`, `--primary-model`, `--delegate-model`, `--aux-model`, `--solver-model` **до** `--apply`. Для повторной генерации используйте новый дом; `--backup-existing --apply` заменяет файлы, сохранив `.backup`, но **не объединяет** старую конфигурацию.
3. По желанию установите проектную политику: `python3 scripts/render.py --home "$SANDBOX" --project "$(pwd)"` (предпросмотр), затем `--apply`, если целевые файлы ещё не существуют. При уже созданном доме проще вручную скопировать `policy/.hermes.md` в рабочий проект.
4. После настройки моделей и авторизации выполните `HERMES_HOME="$SANDBOX" hermes kanban init`, затем в **отдельном терминале** запустите `HERMES_HOME="$SANDBOX" hermes gateway run` и оставьте его работающим. В первом терминале проверьте `HERMES_HOME="$SANDBOX" hermes gateway status`. Не устанавливайте фоновую службу для временного дома: `gateway install` может изменять постоянную службу пользователя; перед её установкой на постоянном доме проверьте существующую службу и её путь. Только после проверки авторизации `solver` создайте карточку `HERMES_HOME="$SANDBOX" hermes kanban create "Inspect a bounded task" --assignee solver --body "Return evidence and limitations; do not edit files." --completion-contract local-only`. **Создание карточки может запустить платный запрос к модели.** Проверьте `HERMES_HOME="$SANDBOX" hermes kanban show TASK_ID` и `HERMES_HOME="$SANDBOX" hermes kanban runs TASK_ID`.

Профиль `solver` имеет свой файл конфигурации, но не полную изоляцию авторизации: при отсутствии собственных записей Hermes может читать `auth.json` **корня этого дома** для того же провайдера. Настройка корня иногда достаточна; проверьте доступ `solver` до запуска карточки, при необходимости настройте профиль отдельно через `HERMES_HOME="$SANDBOX" hermes --profile solver auth ...` (см. `hermes auth --help`). По умолчанию дочерние агенты **не** получают автоматическое разрешение на опасные команды (`subagent_auto_approve: false`), а автоматическая декомпозиция Kanban отключена. Для полного повторения исходной локальной настройки эти параметры надо сознательно изменить после оценки риска. Проектная политика не переносится автоматически в изолированное рабочее пространство карточки; передайте ключевые ограничения в тело задачи. Тесты офлайн: `python3 -m unittest discover -s tests -v`; они не используют платные запросы и не меняют `~/.hermes`.

Актуальная [документация Hermes](https://hermes-agent.nousresearch.com/docs) важнее этого снимка; сравнивайте команды и формат настроек с установленной версией.

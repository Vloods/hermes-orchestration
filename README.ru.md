![Hermes Orchestration](assets/banner.svg)

# Hermes Orchestration

**Чёткая роль каждому агенту — окончательное решение остаётся за человеком.** Небольшой набор конфигурации и проектных правил для Hermes Agent: супервизор, короткие делегированные задачи, постоянная Kanban-доска для профилей-специалистов и отдельный канал вспомогательных вызовов. Это не новый рантайм.

[English](README.md) · [Настройка](docs/setup.md) · [Архитектура](docs/architecture.md) · [Безопасность](docs/security.md)

![Схема маршрутизации](assets/architecture.svg)

## Начало работы

**Hermes уже установлен?** Перед изменениями проверьте настройки и следуйте [инструкции по объединению](docs/setup.md#route-a--hermes-already-installed). Скрипт сначала показывает изменяемые ключи без записи, при явном `--apply` объединяет YAML и сохраняет резервные копии. Описание существующего профиля `solver` не заменяется.

**Устанавливаете Hermes впервые?** Следуйте [маршруту новой установки](docs/setup.md#route-b--fresh-hermes-installation). Обычная цель — `~/.hermes`; авторизация выполняется официальной командой `hermes setup`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/render.py   # только предпросмотр, по умолчанию ~/.hermes
# После проверки моделей повторите с --apply и нужными параметрами.
```

Имена `astra` / `sol` / `luna` — пример одной конфигурации, а не гарантия доступа. Задайте поддерживаемые модели через `--provider`, `--primary-model`, `--delegate-model`, `--aux-model`, `--solver-model`; при предпросмотре и применении используйте одинаковые аргументы. `solver` не назначается автоматически. Установка и тесты не вызывают платные модели.

Подробности: [русское руководство](docs/guide.ru.md), [архитектура](docs/architecture.md), [политика проекта](policy/.hermes.md) и [полная исходная политика](policy/reference.hermes.md). Конфигурация и политика — разные вещи.

## Сообщество

Вопросы и предложения — в [GitHub Issues](https://github.com/Vloods/hermes-orchestration/issues). Это независимый проект, не связанный с Nous Research. Актуальные правила Hermes — в [официальной документации](https://hermes-agent.nousresearch.com/docs).

## Участие

Условия и офлайн-тесты описаны в [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

Оригинальные материалы репозитория распространяются по [MIT](LICENSE); лицензия не распространяется на upstream Hermes Agent.

## Цитирование

Для ссылки на проект используйте [CITATION.cff](CITATION.cff); DOI не заявлен.

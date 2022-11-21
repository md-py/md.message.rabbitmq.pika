# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased

- Switch task processing finish trigger to `queue.Queue().join()` instead of `time.sleep(2.0)`

## [0.3.1] - 2022-11-21
### Fix
#### Documentation

- usage example in documentation fixed according to the latest changes 

## [0.3.0] - 2022-11-01

- Upgrade `md.message` component up to [0.2.0](https://github.com/md-py/md.message/blob/master/changelog.md#0.2.0) from
  [0.1.0](https://github.com/md-py/md.message/blob/master/changelog.md#0.1.0)

## [0.2.0] - 2022-10-31
### Change
#### Backward compatibility breaking change

- Make `md.message.rabbitmq.pika.Message` constructor parameters
  (`channel`, `method_frame`, `header_frame`) optional.
  Useful in case of message creation for sending.
- Changed `md.message.rabbitmq.pika.Message` constructor parameters order

### Fix
#### Documentation

- Fixed typo in package name in documentation

## [0.1.0] - 2022-10-26

- Implementation initialization

[0.3.1]: https://github.com/md-py/md.message.rabbitmq.pika/releases/tag/0.3.1
[0.3.0]: https://github.com/md-py/md.message.rabbitmq.pika/releases/tag/0.3.0
[0.2.0]: https://github.com/md-py/md.message.rabbitmq.pika/releases/tag/0.2.0
[0.1.0]: https://github.com/md-py/md.message.rabbitmq.pika/releases/tag/0.1.0

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Multiprocessing file handler

Source: https://gist.github.com/JesseBuesking/10674086
"""
import multiprocessing
import threading
import logging
import sys
import traceback

from logging.handlers import RotatingFileHandler


class MultiProcessingFileHandler(logging.Handler):

    def __init__(self, name, mode, maxsize, rotate):
        logging.Handler.__init__(self)

        self._handler = RotatingFileHandler(name, mode, maxsize, rotate)
        self.queue = multiprocessing.Queue(-1)

        t = threading.Thread(target=self._receive, name=name)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def _receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except (EOFError, OSError):
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def _format_record(self, record):
        # Ensure that exc_info and args have been stringified. Removes any
        # chance of un-pickleable things inside and possibly reduces message
        # size sent over the pipe.
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None
        return record

    def _send(self, s):
        self.queue.put_nowait(s)

    def emit(self, record):
        try:
            s = self._format_record(record)
            self._send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)

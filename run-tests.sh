#!/bin/sh

coverage run -m unittest discover
coverage xml

#!/bin/bash
mytoken=1234567
curl --data "token=$mytoken" http://localhost:8000/q/generalstat/

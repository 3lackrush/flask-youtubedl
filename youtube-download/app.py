#!-*- coding: utf-8 -*-
'''
今日小计划，利用Celery 和 Youtube-dl 实现Youtube视频下载功能！并且更新博客。
'''

import subprocess
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from wtforms import Form, TextField, validators,PasswordField
from flask_bootstrap import Bootstrap
from celery import Celery


app = Flask(__name__)
Bootstrap(app)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


class LoginForm(Form):
	username = TextField("username", [validators.Required()])
	password = PasswordField("password", [validators.Required()])


class YoutubeUrl(Form):
	download_url = TextField("download_url", [validators.Required()])
	socks5Proxy = TextField("socks5Proxy", [validators.Required()])

@celery.task
def downloadVideo(url,proxy_address):
	msg = "Url: {0}, Proxy address: {1}".format(url, proxy_address)
	newCommand = "youtube-dl --proxy=%s %s"%(proxy_address,url)
	subprocess.Popen(newCommand, stdout=subprocess.PIPE, shell=True) 



@app.route('/', methods=['GET','POST'])
def index():
	myForm = YoutubeUrl(request.form)
	msg = []
	if request.method == 'POST':
		download_url = myForm.download_url.data
		socks5Proxy = myForm.socks5Proxy.data

		if myForm.validate():
			celery_task_id = downloadVideo.delay(download_url, socks5Proxy)
			msg = [celery_task_id,download_url, socks5Proxy]
			return render_template('index.html', download_task_msg=msg, form=myForm)
		else:
			return render_template('index.html',download_task_msg=msg, form=myForm)
	return render_template('index.html',download_task_msg=msg, form=myForm)



if __name__ == '__main__':
	app.run(debug=True)
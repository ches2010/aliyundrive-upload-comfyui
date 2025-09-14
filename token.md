### 以下是我在海纳思社区找到的教程 

[小雅安装教程|海纳思系统](https://doc.ecoo.top/docs/nas-skill/xiaoya/ "小雅安装教程|海纳思系统")

**一、准备转存阿里云盘文件夹**

1.手机下载安装阿里云盘 APP

![下载阿里云盘APP](https://doc.ecoo.top/assets/images/xiaoya1-9cd37baeb33af3af0b69d49aaec19169.jpg)

2、注册登录阿里云盘

![注册登录阿里云盘](https://doc.ecoo.top/assets/images/xiaoya2-b58d68ba81e3fe80bb50dd0fbf05308a.png)

3、电脑浏览器打开阿里云盘官网

[点击此处前往登录](https://www.alipan.com "登录")

4、使用手机上的阿里云盘 App 扫码登录

![扫码登陆](https://doc.ecoo.top/assets/images/xiaoya3-4c62b712dbad8acd8c8fddd86a7ccc70.png)

5、创建小雅缓存的文件夹

文件名可以自行定义，注意不能使用 备份盘 ，必须使用 资源库

![创建文件夹](https://doc.ecoo.top/assets/images/xiaoya4-f51a4a68790245cd4d3d61760f77fc2a.png)


6、获取所需的 `folderId`

获得转存文件夹参数 `folderId`，将这串数字复制保存。
![获取folderId](https://doc.ecoo.top/assets/images/xiaoya5-eef1603b72ee93c35eab16034ee17054.jpg)


**二、获取 refreshToken（32 位长）**
访问链接扫码登录即可获取，这是海纳思系统网站建立的代理地址：

[点击 csb.histb.com 此处前往获取 refreshToken](https://csb.histb.com/ "refreshToken")

将这串字符复制保存

![获取 refreshToken（32 位长）](https://doc.ecoo.top/assets/images/xiaoya6-c1730350567ba020e16c73e4cddf2d95.png)


**三、获取 token（280 位长）**

[点击此处前往获取 token](https://alist.nn.ci/tool/aliyundrive/request.html "token")

点击按钮,生成登录二维码

![获取token](https://doc.ecoo.top/assets/images/xiaoya7-e116ae5e9a82a62b5193ea8f41a0fe16.png)

手机扫码授权

![手机扫码授权](https://doc.ecoo.top/assets/images/xiaoya8-fbab93b4619a1c038d1ea2b839450fcc.jpg)

授权完成后点击按钮生成 `280 位 token`

![点击按钮生成280位token](https://github.com/ches2010/ComfyUI_aliupload/blob/main/aliyun/token.png)

复制保存` token（280 位）`

![保持token](https://doc.ecoo.top/assets/images/xiaoya10-604a5d6ca332a296e42a0e4597d47e59.png)

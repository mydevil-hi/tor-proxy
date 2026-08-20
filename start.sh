#!/bin/bash

# تشغيل Tor بالخلفية
tor &

# الانتظار حتى يكتمل اتصال Tor بالشبكة
echo "⏳ جاري الاتصال بشبكة Tor..."
while ! nc -z 127.0.0.1 9050; do   
  sleep 1
done
echo "✅ تم الاتصال بشبكة Tor بنجاح!"

# تشغيل خادم البايثون
python server.py

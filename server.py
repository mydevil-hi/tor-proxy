import base64
import os
from aiohttp import web, ClientSession
from aiohttp_socks import ProxyConnector

# بيانات المصادقة (يمكنك تغييرها هنا)
PROXY_USER = os.getenv("PROXY_USER", "devil")
PROXY_PASS = os.getenv("PROXY_PASS", "devil123")

# منفذ Tor المحلي
TOR_SOCKS = "socks5://127.0.0.1:9050"


async def handle_proxy(request):
    # 1. التحقق من اليوزر والباسورد
    auth_header = request.headers.get("Proxy-Authorization")
    if not auth_header:
        return web.Response(
            status=407,
            headers={"Proxy-Authenticate": 'Basic realm="Tor Proxy Gateway"'},
        )

    try:
        auth_type, encoded = auth_header.split(" ", 1)
        decoded = base64.b64decode(encoded).decode("utf-8")
        user, password = decoded.split(":", 1)

        if user != PROXY_USER or password != PROXY_PASS:
            return web.Response(status=403, text="❌ خطأ في اليوزر أو الباسورد")
    except Exception:
        return web.Response(status=400, text="❌ تنسيق طلب غير صحيح")

    # 2. إرسال الطلب عبر Tor لضمان الحصول على IP متدوّر
    connector = ProxyConnector.from_url(TOR_SOCKS)
    async with ClientSession(connector=connector) as session:
        try:
            # تجهيز الهيدرز بدون Proxy-Authorization لمنع تسريبها للموقع المستهدف
            headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower() != "proxy-authorization"
            }

            async with session.request(
                method=request.method,
                url=request.url,
                headers=headers,
                data=await request.read(),
                timeout=15,
            ) as response:
                body = await response.read()
                return web.Response(
                    body=body, status=response.status, headers=response.headers
                )
        except Exception as e:
            return web.Response(status=502, text=f"❌ خطأ في شبكة Tor: {str(e)}")


app = web.Application()
app.router.add_route("*", "/{path:.*}", handle_proxy)

if __name__ == "__main__":
    # Koyeb يقدم البورت في المتغير البيئي PORT تلقائياً
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
  

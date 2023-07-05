import requests

cf_request_event = {
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/api/items/555",
    "rawQueryString": "q=boo",
    "headers": {
        "cloudfront-is-android-viewer": "false",
        "cloudfront-viewer-country": "US",
        "x-amzn-tls-version": "TLSv1.2",
        "sec-fetch-site": "none",
        "cloudfront-viewer-postal-code": "44119",
        "cloudfront-viewer-tls": "TLSv1.3:TLS_AES_128_GCM_SHA256:fullHandshake",
        "x-forwarded-port": "443",
        "sec-fetch-user": "?1",
        "via": "2.0 ee57d6770700357db4b696b4c5250b82.cloudfront.net (CloudFront)",
        "x-amzn-tls-cipher-suite": "ECDHE-RSA-AES128-GCM-SHA256",
        "sec-ch-ua-mobile": "?0",
        "cloudfront-is-desktop-viewer": "true",
        "cloudfront-viewer-asn": "7018",
        "cloudfront-viewer-country-name": "United States",
        "host": "xnn2voft2wbn7eyfqrnkow2gg40xycus.lambda-url.us-east-2.on.aws",
        "upgrade-insecure-requests": "1",
        "cache-control": "max-age=0",
        "cloudfront-viewer-city": "Cleveland",
        "sec-fetch-mode": "navigate",
        "cloudfront-viewer-http-version": "2.0",
        "accept-language": "en-US,en;q=0.9",
        "cloudfront-viewer-address": "2600:1700:6640:e4d0:29c0:9cf7:9107:5eca:50235",
        "x-forwarded-proto": "https",
        "cloudfront-is-ios-viewer": "false",
        "cloudfront-viewer-metro-code": "510",
        "x-forwarded-for": "2600:1700:6640:e4d0:29c0:9cf7:9107:5eca",
        "cloudfront-viewer-country-region": "OH",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "cloudfront-viewer-time-zone": "America/New_York",
        "cloudfront-is-smarttv-viewer": "false",
        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "x-amzn-trace-id": "Root=1-647cef1a-4937ab91132730a238bbdaa6",
        "cloudfront-viewer-longitude": "-81.54920",
        "cloudfront-is-tablet-viewer": "false",
        "sec-ch-ua-platform": '"macOS"',
        "cloudfront-forwarded-proto": "https",
        "cloudfront-viewer-latitude": "41.58820",
        "cloudfront-viewer-country-region-name": "Ohio",
        "accept-encoding": "gzip, deflate, br",
        "x-amz-cf-id": "oexs8TSd7pccNPrijTKorXl6PqvJRgRTROgup8zoyu2k28l8HT7f3Q==",
        "cloudfront-is-mobile-viewer": "false",
        "sec-fetch-dest": "document",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    },
    "queryStringParameters": {"q": "boo"},
    "requestContext": {
        "accountId": "anonymous",
        "apiId": "xnn2voft2wbn7eyfqrnkow2gg40xycus",
        "domainName": "xnn2voft2wbn7eyfqrnkow2gg40xycus.lambda-url.us-east-2.on.aws",
        "domainPrefix": "xnn2voft2wbn7eyfqrnkow2gg40xycus",
        "http": {
            "method": "GET",
            "path": "/api/items/555",
            "protocol": "HTTP/1.1",
            "sourceIp": "15.158.47.172",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        },
        "requestId": "66c6f5ee-eafc-402f-95ca-1ec5343eea00",
        "routeKey": "$default",
        "stage": "$default",
        "time": "04/Jun/2023:20:07:54 +0000",
        "timeEpoch": 1685909274380,
    },
    "isBase64Encoded": False,
}


def main():
    resp = requests.post(
        "http://localhost:9000/2015-03-31/functions/function/invocations",
        json=cf_request_event,
    )
    import pdb

    pdb.set_trace()
    print(resp)
    print(resp.json())


if __name__ == "__main__":
    main()

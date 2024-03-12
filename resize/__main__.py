import asyncio

from resize.main import ImageResizer

if __name__ == "__main__":
    asyncio.run(ImageResizer().run())

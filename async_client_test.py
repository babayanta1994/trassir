"module for testing writing and erasing cards from trueip server"

import asyncio
import logging
import json
import aiohttp

HOST = "195.182.143.57"
PORT = 5002
SCHEME = "http"
LOGIN = "admin"
PASSWORD = "admin123"


def logger():
    "logging helper"
    return logging.getLogger(__name__)


def check_field(value, field, type_list):
    "check presence and type of a field in a dict"
    if not isinstance(value, dict):
        raise RuntimeError("not a dict (%s)" % value)
    if field not in value:
        raise RuntimeError("field '%s' is missing (%s)" % (field, value))
    for item_type in type_list:
        if isinstance(value[field], item_type):
            return
    raise RuntimeError("field '%s' is not %s (%s)" % (field, type_list, value))


def check_keys(value, keys):
    "check if dict has expected set of keys"
    if not isinstance(value, dict):
        raise RuntimeError("not a dict (%s)" % value)
    if set(value.keys()) != set(keys):
        raise RuntimeError("expected keys %s but got %s" % (keys, value.keys()))


def make_url(path):
    "makes url SCHEME://HOST:PORT/path"
    return "%s://%s:%d/%s" % (SCHEME, HOST, PORT, path)


async def async_post(session, handler, data, validator):
    "aiohttp post wrapper"
    logger().info("POST '%s' data = (%s)", handler, data)
    async with session.post(make_url(handler), json=data) as resp:
        result = await resp.text()
        if resp.status == 200:
            try:
                json_result = json.loads(result)
                if json_result["success"] == 1 and validator(json_result):
                    logger().info(
                        "response for '%s' data = (%s): %s",
                        handler,
                        data,
                        result
                    )
                    return json_result
            except RuntimeError as exc:
                logger().error("async_post exception: %s", exc)
        logger().error("FAILED")
        logger().error("url: %s", make_url(handler))
        logger().error("status: %s", resp.status)
        logger().error("sent params: %s", data)
        logger().error("result: %s", result)
        if resp.status == 200 and not validator(result):
            logger().error("VALIDATION FAILED")
        raise RuntimeError("%s FAILED" % handler)


async def auth(session, login, password):
    "trueip auth request"
    def validator(res):
        try:
            check_keys(res, ["success", "sid"])
            check_field(res, "success", [int, bool])
            check_field(res, "sid", [str])
            return True
        except RuntimeError as exc:
            logger().error("authorize validation exception: %s", exc)
        return False
    data = {"login": login, "password": password}
    res = await async_post(session, "authorize", data, validator)
    return res["sid"]


async def get_devices(session, sid):
    "trueip get_devices request"
    def validator(res):
        try:
            check_keys(res, ["success", "devices"])
            check_field(res, "success", [int, bool])
            check_field(res, "devices", [list])
            devices = res["devices"]
            for dev in devices:
                check_keys(dev, ["device_id", "device_name", "device_online"])
                check_field(dev, "device_id", [str])
                check_field(dev, "device_name", [str])
                check_field(dev, "device_online", [int])
            return True
        except RuntimeError as exc:
            logger().error("get_devices validation exception: %s", exc)
        return False
    data = {"sid": sid}
    res = await async_post(session, "get_devices", data, validator)
    return res["devices"]


async def get_cards(session, sid, device_id):
    "trueip get_cards request"
    def validator(res):
        try:
            check_keys(res, ["success", "cards"])
            check_field(res, "success", [int, bool])
            check_field(res, "cards", [list])
            cards = res["cards"]
            for card in cards:
                check_keys(card, ["card_id", "person_name"])
                check_field(card, "card_id", [str])
                check_field(card, "person_name", [str])
            return True
        except RuntimeError as exc:
            logger().error("get_cards validation exception: %s", exc)
        return False
    data = {"sid": sid, "device_id": device_id}
    res = await async_post(session, "get_cards", data, validator)
    return {"device_id": device_id, "cards": res["cards"]}


async def set_cards(session, sid, device_id, cards_info):
    "trueip set_cards request"
    def validator(res):
        try:
            check_keys(res, ["success", "written_cards", "failed_cards"])
            check_field(res, "success", [int, bool])
            check_field(res, "written_cards", [list])
            written_cards = res["written_cards"]
            for card in written_cards:
                if not isinstance(card, str):
                    raise RuntimeError("written_cards item is not a str: %s" % type(card))
            check_field(res, "failed_cards", [list])
            failed_cards = res["failed_cards"]
            for error in failed_cards:
                check_field(error, "cards_ids", [list])
                check_field(error, "error_code", [int])
                check_field(error, "description", [str])
                for card in error["cards_ids"]:
                    if not isinstance(card, str):
                        raise RuntimeError("failed cards_ids item is not a str: %s" % type(card))
            return True
        except RuntimeError as exc:
            logger().error("set_cards validation exception: %s", exc)
        return False
    data = {"sid": sid, "device_id": device_id, "cards": cards_info}
    res = await async_post(session, "set_cards", data, validator)
    return res is not None


async def erase_cards(session, sid, device_id, cards):
    "trueip erase_cards request"
    def validator(res):
        try:
            check_field(res, "success", [int, bool])
            check_field(res, "deleted_cards", [list])
            deleted_cards = res["deleted_cards"]
            for card in deleted_cards:
                if not isinstance(card, str):
                    raise RuntimeError("written_cards item is not a str: %s" % type(card))
            failed_cards = res.get("failed_cards", [])
            for card in failed_cards:
                if not isinstance(card, str):
                    raise RuntimeError("failed_cards item is not a str: %s" % type(card))
            return True
        except RuntimeError as exc:
            logger().error("erase_cards validation exception: %s", exc)
        return False
    data = {"sid": sid, "device_id": device_id, "cards": cards}
    res = await async_post(session, "erase_cards", data, validator)
    return res is not None


async def do_test():
    "test writing and erasing cards from trueip server"
    try:
        session = aiohttp.ClientSession()
        sid = await auth(session, LOGIN, PASSWORD)
        devices = await get_devices(session, sid)

        test_card = "7E57C0DE"
        test_cards = [{"card_id": test_card, "person_name": "Test Person"}]

        await asyncio.gather(
            *(set_cards(session, sid, dev["device_id"], test_cards) for dev in devices)
        )
        cards_by_devices = await asyncio.gather(
            *(get_cards(session, sid, dev["device_id"]) for dev in devices)
        )
        for item in cards_by_devices:
            device_cards = item["cards"]
            for card in test_cards:
                if card not in device_cards:
                    logger().error("test card: %s", card)
                    logger().error("device cards: %s", device_cards)
                    raise RuntimeError("failed to write card to " + item["device_id"])

        await asyncio.gather(
            *(erase_cards(session, sid, dev["device_id"], [test_card]) for dev in devices)
        )
        cards_by_devices = await asyncio.gather(
            *(get_cards(session, sid, dev["device_id"]) for dev in devices)
        )
        for item in cards_by_devices:
            device_cards = item["cards"]
            for card in test_cards:
                if card in device_cards:
                    logger().error("test card: %s", card)
                    logger().error("device cards: %s", device_cards)
                    raise RuntimeError("failed to erase card from " + item["device_id"])
        logger().info("DONE")
    except RuntimeError as exc:
        logger().error("test exception: %s", exc)
        raise
    finally:
        await session.close()


def main():
    "entry point"
    logging.basicConfig(
        filename="async_client_test.log",
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_test())


if __name__ == "__main__":
    main()

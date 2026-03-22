"""Image upload module for generating test data."""

import asyncio
import io
import pathlib
from secrets import SystemRandom

import pandas as pd
from fastapi import UploadFile
from fastapi.datastructures import Headers
from internal.block.management import BlockManagement

secure_rng = SystemRandom()


def get_bundle_images() -> list[tuple[str, bytes]]:
    """Load bundle images from the bundle_images directory.

    Returns:
        List of tuples containing (filename, image_bytes).
    """
    bundle_images_path = pathlib.Path(__file__).parent / "bundle_images"
    bundle_images = list(bundle_images_path.glob("*.jpeg"))
    return [(img.name, img.read_bytes()) for img in bundle_images]


def get_profile_images() -> list[tuple[str, bytes]]:
    """Load profile images from the profile_images directory.

    Returns:
        List of tuples containing (filename, image_bytes).
    """
    profile_images_path = pathlib.Path(__file__).parent / "profile_images"
    profile_images = list(profile_images_path.glob("*.jpeg"))
    return [(img.name, img.read_bytes()) for img in profile_images]


async def upload_bundle_images(
    bundle_ids: list[int], image_data: list[tuple[str, bytes]]
) -> None:
    """Upload bundle images to block storage.

    Args:
        bundle_ids: List of bundle IDs to upload images for.
        image_data: List of tuples containing (filename, image_bytes).
    """
    block_management = BlockManagement()
    block_management.initialise()

    total = len(bundle_ids)
    for i, bundle_id in enumerate(bundle_ids, start=1):
        name, content = secure_rng.choice(image_data)
        file = UploadFile(
            filename=name,
            file=io.BytesIO(content),
            headers=Headers({"content-type": "image/jpeg"}),
        )
        await block_management.upload_bundle_image(bundle_id, file)
        print(f"   Uploading bundle images: {i}/{total}", end="\r")
    print()


async def upload_profile_images(
    user_ids: list[int], image_data: list[tuple[str, bytes]]
) -> None:
    """Upload profile images to block storage.

    Args:
        user_ids: List of user IDs to upload images for.
        image_data: List of tuples containing (filename, image_bytes).
    """
    block_management = BlockManagement()
    block_management.initialise()

    total = len(user_ids)
    for i, user_id in enumerate(user_ids, start=1):
        name, content = secure_rng.choice(image_data)
        file = UploadFile(
            filename=name,
            file=io.BytesIO(content),
            headers=Headers({"content-type": "image/jpeg"}),
        )
        await block_management.upload_profile_image(user_id, file)
        print(f"   Uploading profile images: {i}/{total}", end="\r")
    print()


async def upload_images_for_bundles(
    bundles_csv_path: str = "synthetic_data/bundles.csv",
) -> None:
    """Upload images for all bundles in the bundles CSV file.

    Args:
        bundles_csv_path: Path to the bundles CSV file.
    """
    image_data = get_bundle_images()
    df_bundles = pd.read_csv(bundles_csv_path)
    bundle_ids = df_bundles["bundle_id"].tolist()

    print(f"   Uploading {len(bundle_ids)} bundle images...")
    await upload_bundle_images(bundle_ids, image_data)


async def upload_images_for_users(
    users_csv_path: str = "synthetic_data/users.csv",
) -> None:
    """Upload images for all users in the users CSV file.

    Args:
        users_csv_path: Path to the users CSV file.
    """
    image_data = get_profile_images()
    df_users = pd.read_csv(users_csv_path)
    user_ids = df_users["user_id"].tolist()

    print(f"   Uploading {len(user_ids)} profile images...")
    await upload_profile_images(user_ids, image_data)


async def upload_all_images(
    bundles_csv_path: str = "synthetic_data/bundles.csv",
    users_csv_path: str = "synthetic_data/users.csv",
) -> None:
    """Upload all images (bundles and profiles) from CSV files.

    Args:
        bundles_csv_path: Path to the bundles CSV file.
        users_csv_path: Path to the users CSV file.
    """
    await upload_images_for_bundles(bundles_csv_path)
    await upload_images_for_users(users_csv_path)


if __name__ == "__main__":
    asyncio.run(upload_all_images())

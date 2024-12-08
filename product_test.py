import pytest
from fastapi.testclient import TestClient
from unittest import mock
from main import app
from repository.product_repository import ProductRepository

# 使用 TestClient 進行測試
happyclient = TestClient(app)

# 測試函數
def test_create_product(mocker):
    # 模擬 ProductRepository.create_product 方法，假設返回 1
    mock_create_product = mocker.patch.object(ProductRepository, "create_product", return_value=1)
    
    # 進行 POST 請求，並檢查響應
    response = happyclient.post("/product/", json={
        "id": 1,
        "name": "test",
        "price": 100,
        "color": "red",
        "size": "M",
        "remain_amount": 100,
        "description": "test",
        "categories": "test",
        "discount": 0,
        "image_url": "test"
    })

    # 驗證 API 響應
    assert response.status_code == 200
    assert response.json() == 1

    # 確保 mock 函數被正確調用
    mock_create_product.assert_called_once_with({
        "id": 1,
        "name": "test",
        "price": 100,
        "color": "red",
        "size": "M",
        "remain_amount": 100,
        "description": "test",
        "categories": "test",
        "discount": 0,
        "image_url": "test"
    })

"""
HS编码查询 API 服务 - FastAPI 版本
提供 RESTful API 接口供 AI 智能体调用
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List
import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import HSCodeScraper
from src.utils import setup_logger

# 设置日志
logger = setup_logger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(
    title="HS 编码查询 API",
    description="根据商品名称查询海关 HS 编码及详细信息",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 scraper 实例
scraper = None


def get_scraper():
    """获取或创建 scraper 实例"""
    global scraper
    if scraper is None:
        scraper = HSCodeScraper()
        logger.info("HSCodeScraper 实例已创建")
    return scraper


# Pydantic 模型
class ProductQueryRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('product_name')
    def validate_name(cls, v):
        return v.strip()


class BatchQueryRequest(BaseModel):
    product_names: List[str] = Field(..., min_items=1, max_items=50)


class HSCodeQueryRequest(BaseModel):
    hs_code: str = Field(..., min_length=1, max_length=20)
    
    @validator('hs_code')
    def validate_code(cls, v):
        return v.strip()


# API 路由
@app.get("/")
async def index():
    """API 首页"""
    return {
        'service': 'HS 编码查询 API',
        'version': '1.0.0',
        'status': 'running',
        'docs': '/docs'
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {'status': 'ok'}


@app.post("/api/query")
async def query(req: ProductQueryRequest):
    """查询商品 HS 编码"""
    try:
        logger.info(f"查询: {req.product_name}")
        result = get_scraper().query_by_product_name(req.product_name)
        
        if result.get('search_success'):
            return {'success': True, 'data': result}
        else:
            raise HTTPException(
                status_code=404,
                detail={'success': False, 'error': result.get('error_message')}
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询异常: {e}")
        raise HTTPException(status_code=500, detail={'error': str(e)})


@app.post("/api/batch_query")
async def batch_query(req: BatchQueryRequest):
    """批量查询"""
    try:
        results = get_scraper().batch_query(req.product_names)
        successful = sum(1 for r in results if r.get('search_success'))
        
        return {
            'success': True,
            'total': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'results': results
        }
    except Exception as e:
        logger.error(f"批量查询异常: {e}")
        raise HTTPException(status_code=500, detail={'error': str(e)})


@app.post("/api/query_by_code")
async def query_by_code(req: HSCodeQueryRequest):
    """根据 HS 编码查询"""
    try:
        result = get_scraper().query_by_hs_code(req.hs_code)
        
        if result.get('search_success'):
            return {'success': True, 'data': result}
        else:
            raise HTTPException(
                status_code=404,
                detail={'success': False, 'error': result.get('error_message')}
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询异常: {e}")
        raise HTTPException(status_code=500, detail={'error': str(e)})


@app.on_event("startup")
async def startup():
    logger.info("API 服务启动 - http://0.0.0.0:8000/docs")


@app.on_event("shutdown")
async def shutdown():
    global scraper
    if scraper:
        scraper.close()
    logger.info("API 服务关闭")


if __name__ == '__main__':
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)


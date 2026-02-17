from pydantic import BaseModel, Field

class SponsorPackage(BaseModel):
    title: str = Field(description="패키지명")
    target: str = Field(description="타깃 후원사 유형")
    price_krw: int = Field(description="가격(원)")
    benefits: list[str] = Field(description="혜택")
    risks: list[str] = Field(description="리스크")

class SponsorPackageList(BaseModel):
    packages: list[SponsorPackage]

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from app.interfaces.schemas.__init__ import Agreement, AgreementProduct, AgreementStoreRule, AgreementExcludedFlag
from app.interfaces.schemas.agreement_schema import AgreementSearchRequest, AgreementSearchResponse


class AgreementRepository(ABC):

    @abstractmethod
    async def create_agreement(self, agreement: Agreement) -> Agreement:
        pass

    @abstractmethod
    async def create_agreement_product(self, product: AgreementProduct) -> AgreementProduct:
        pass

    @abstractmethod
    async def create_agreement_store_rule(self, store_rule: AgreementStoreRule) -> AgreementStoreRule:
        pass

    @abstractmethod
    async def create_agreement_excluded_flag(self, excluded_flag: AgreementExcludedFlag) -> AgreementExcludedFlag:
        pass

    @abstractmethod
    async def exists_agreement_by_number_and_business_unit(
        self, 
        agreement_number: int, 
        business_unit_id: int
    ) -> bool:
        pass

    @abstractmethod
    async def search_agreements(self, search_request: AgreementSearchRequest) -> AgreementSearchResponse:
        pass

    @abstractmethod
    async def get_agreement_by_id(self, agreement_id: int) -> Optional[Agreement]:
        pass

    @abstractmethod
    async def get_agreement_with_details(self, agreement_id: int) -> Optional[Tuple[Agreement, List[AgreementProduct], List[AgreementStoreRule], List[AgreementExcludedFlag]]]:
        pass

    @abstractmethod
    async def create_complete_agreement(
        self,
        agreement: Agreement,
        products: List[AgreementProduct],
        store_rules: List[AgreementStoreRule],
        excluded_flags: List[AgreementExcludedFlag]
    ) -> Tuple[Agreement, List[AgreementProduct], List[AgreementStoreRule], List[AgreementExcludedFlag]]:
        pass

    @abstractmethod
    async def update_complete_agreement(
        self,
        agreement_id: int,
        agreement: Agreement,
        products: List[AgreementProduct],
        store_rules: List[AgreementStoreRule],
        excluded_flags: List[AgreementExcludedFlag]
    ) -> Tuple[Agreement, List[AgreementProduct], List[AgreementStoreRule], List[AgreementExcludedFlag]]:
        pass
        pass

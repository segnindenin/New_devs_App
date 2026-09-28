from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    # FIX Bug #3: Do NOT convert to float — float is IEEE 754 binary which introduces
    # rounding errors on decimal values (e.g. 333.333 + 333.333 + 333.334 becomes 999.9999...)
    # Use Decimal with proper rounding to 2 decimal places for financial data.
    total_revenue_decimal = Decimal(str(revenue_data['total'])).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": str(total_revenue_decimal),  # Return as string to preserve precision
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }

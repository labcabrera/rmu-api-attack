"""
RSQL (RESTful Service Query Language) parser for attack queries.
This module provides functionality to parse RSQL expressions into MongoDB queries.
"""

import re
from typing import Dict, Any, Optional, Union
from enum import Enum


class RSQLOperator(Enum):
    """RSQL operators"""

    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = "=gt="
    GREATER_EQUAL = "=ge="
    LESS_THAN = "=lt="
    LESS_EQUAL = "=le="
    IN = "=in="
    OUT = "=out="
    LIKE = "=like="


class RSQLParser:
    """Parser for RSQL query expressions"""

    RSQL_PATTERN = (
        r"(\w+)(==|!=|=gt=|=ge=|=lt=|=le=|=in=|=out=|=like=)(\([^)]+\)|[^;,&|]+)"
    )

    @classmethod
    def parse(cls, rsql_query: Optional[str]) -> Dict[str, Any]:
        """
        Parse RSQL query string into MongoDB query dict

        Examples:
        - 'status==DRAFT' -> {'status': 'DRAFT'}
        - 'actionId==action_001;sourceId==source_001' -> {'actionId': 'action_001', 'sourceId': 'source_001'}
        - 'status=in=(DRAFT,APPLIED)' -> {'status': {'$in': ['DRAFT', 'APPLIED']}}
        """

        if not rsql_query or not rsql_query.strip():
            return {}

        # For now, implement a simple parser that supports basic operations
        # In a production system, you might want to use a proper RSQL parser library

        query_dict = {}

        # Split by logical AND (semicolon or 'and')
        and_parts = re.split(r"[;&]|\sand\s", rsql_query)

        for part in and_parts:
            part = part.strip()
            if not part:
                continue

            match = re.match(cls.RSQL_PATTERN, part)
            if match:
                field, operator, value = match.groups()
                field = field.strip()
                value = value.strip()

                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

                query_dict.update(cls._convert_to_mongo_query(field, operator, value))

        return query_dict

    @classmethod
    def _convert_to_mongo_query(
        cls, field: str, operator: str, value: str
    ) -> Dict[str, Any]:
        """Convert RSQL field-operator-value to MongoDB query"""

        if operator == RSQLOperator.EQUAL.value:
            return {field: value}

        elif operator == RSQLOperator.NOT_EQUAL.value:
            return {field: {"$ne": value}}

        elif operator == RSQLOperator.GREATER_THAN.value:
            return {field: {"$gt": cls._convert_value(value)}}

        elif operator == RSQLOperator.GREATER_EQUAL.value:
            return {field: {"$gte": cls._convert_value(value)}}

        elif operator == RSQLOperator.LESS_THAN.value:
            return {field: {"$lt": cls._convert_value(value)}}

        elif operator == RSQLOperator.LESS_EQUAL.value:
            return {field: {"$lte": cls._convert_value(value)}}

        elif operator == RSQLOperator.IN.value:
            # Parse comma-separated values: (value1,value2,value3)
            if value.startswith("(") and value.endswith(")"):
                values = value[1:-1].split(",")
                values = [v.strip().strip("\"'") for v in values]
                return {field: {"$in": values}}
            return {field: {"$in": [value]}}

        elif operator == RSQLOperator.OUT.value:
            # Parse comma-separated values: (value1,value2,value3)
            if value.startswith("(") and value.endswith(")"):
                values = value[1:-1].split(",")
                values = [v.strip().strip("\"'") for v in values]
                return {field: {"$nin": values}}
            return {field: {"$nin": [value]}}

        elif operator == RSQLOperator.LIKE.value:
            # Convert to MongoDB regex
            regex_value = value.replace("*", ".*").replace("?", ".")
            return {field: {"$regex": regex_value, "$options": "i"}}

        else:
            # Default to equality
            return {field: value}

    @classmethod
    def _convert_value(cls, value: str) -> Union[str, int, float]:
        """Convert string value to appropriate type"""

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

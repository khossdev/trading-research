from pathlib import Path

from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.persistence.catalog import ParquetDataCatalog


def test_write_and_read_bars(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog"
    catalog = ParquetDataCatalog.from_uri(str(catalog_path))

    instrument_id = InstrumentId.from_str("AAPL.XNAS")
    bar_type = BarType.from_str("AAPL.XNAS-1-MINUTE-LAST-EXTERNAL")

    bars = [
        Bar(
            bar_type,
            Price(100.00, 2),
            Price(101.00, 2),
            Price(99.00, 2),
            Price(100.50, 2),
            Quantity(10, 0),
            1_000_000_000,
            1_000_000_000,
        ),
        Bar(
            bar_type,
            Price(100.50, 2),
            Price(102.00, 2),
            Price(100.00, 2),
            Price(101.50, 2),
            Quantity(12, 0),
            61_000_000_000,
            61_000_000_000,
        ),
        Bar(
            bar_type,
            Price(101.50, 2),
            Price(103.00, 2),
            Price(101.00, 2),
            Price(102.50, 2),
            Quantity(15, 0),
            121_000_000_000,
            121_000_000_000,
        ),
    ]

    catalog.write_data(bars)

    loaded = catalog.bars(
        instrument_ids=[instrument_id],
        bar_types=[bar_type],
    )

    assert len(loaded) == 3
    assert loaded[0].close == Price(100.50, 2)
    assert loaded[-1].close == Price(102.50, 2)
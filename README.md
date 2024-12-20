# Alpaca Based Trading Bot/Platform

A Python-based automated trading platform using Alpaca Markets API for executing algorithmic trading strategies with real-time monitoring and risk management.

## Features

- Automated trade execution via Alpaca API
- Signal-based trading strategy implementation
- Real-time order and position monitoring
- Risk management controls
- Account verification and status monitoring
- Configurable trading parameters

## Project Structure

```
alpaca_trading/
├── pyproject.toml        # Poetry project configuration
├── README.md  
├── .env                  # Environment variables (API keys)
├── src/
│   ├── config.py         # Configuration management
│   ├── models/  
│   │   └── signal.py     # Signal dataclass/model
│   ├── services/
│   │   ├── alpaca_service.py     # Alpaca API wrapper
│   │   ├── signal_processor.py   # Signal processing logic
│   │   └── order_monitor.py      # Order monitoring service
│   ├── utils/
│   │   ├── logger.py     # Logging configuration
│   │   └── validators.py # Input validation
│   └── main.py          # Entry point
└── tests/
    └── test_services/
        └── test_alpaca.py
```

## Installation

1. Clone the repository
2. Install dependencies with Poetry:

```bash
poetry install
```

3. Create `.env` file with your Alpaca credentials:

```
API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

## Usage

1. Verify account setup:

```bash
poetry run python src/verify_setup.py
```

2. Run the trading system:

```bash
poetry run python src/main.py
```

3. Monitor positions and orders:

```bash
poetry run python src/monitoring.py
```

## Configuration

- Minimum signal confidence: 0.5
- Minimum risk/reward ratio: 1.5
- Default monitoring interval: 60 seconds

## Development Status

🚧 This project is under active development. Features are being added and refined regularly.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

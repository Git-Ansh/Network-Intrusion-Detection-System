# NIDS Microservices README

# NIDS Microservices

This directory contains the microservices for the Real-Time Network Intrusion Detection System (NIDS). The microservices are responsible for packet capture and machine learning inference, providing the core functionality of the NIDS suite.

## Directory Structure

```
microservices/
├── packet_capture/
│   ├── src/
│   │   ├── capture.py
│   │   ├── flow_builder.py
│   │   ├── feature_extraction.py
│   │   └── utils.py
│   └── tests/
│       └── test_capture.py
├── ml_engine/
│   ├── src/
│   │   ├── models/
│   │   │   ├── isolation_forest.py
│   │   │   └── random_forest.py
│   │   ├── inference.py
│   │   ├── training.py
│   │   └── utils.py
│   └── tests/
│       └── test_inference.py
├── run_all.py
├── requirements.txt
└── README.md
```

## Overview

The microservices are divided into two main components:

1. **Packet Capture**: This microservice captures network packets, processes them, and extracts relevant features for analysis.
2. **Machine Learning Engine**: This microservice performs machine learning inference on the extracted features to detect anomalies and potential threats.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Required Python packages listed in `requirements.txt`

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/acme/nids-suite.git
   cd nids-suite/microservices
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Microservices

To run both microservices, execute the following command:
```
python run_all.py
```

This will start the packet capture and machine learning services concurrently.

## Testing

Unit tests for both microservices are located in the `tests` directories. To run the tests, ensure you are in the virtual environment and execute:
```
pytest
```

## Contributing

Contributions are welcome! Please follow the standard Git workflow for submitting pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Thanks to the contributors and the open-source community for their support and resources.
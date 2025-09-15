# OneForAll API

A FastAPI-based REST API wrapper for the [OneForAll](https://github.com/shmilylty/OneForAll) subdomain enumeration tool. This service provides a simple HTTP interface to perform subdomain discovery scans and retrieve results in JSON format.

## Features

- 🚀 **REST API Interface**: Easy-to-use HTTP endpoints for subdomain scanning
- 🐳 **Docker Support**: Containerized deployment with Docker Compose
- 📊 **JSON Output**: Structured results in JSON format
- ⚡ **HTTP Requests Option**: Enable/disable HTTP requests during scanning
- 🔍 **Alive Check**: Filter results to only include alive subdomains
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ⏱️ **Timeout Protection**: 5-minute timeout to prevent hanging scans

## Quick Start

### Using Docker Image (Fastest)

Pull and run the pre-built Docker image:

```bash
# Pull the latest image
docker pull ghcr.io/w95/oneforall-api:latest

# Run the container
docker run -d \
  --name oneforall-api \
  -p 9403:9403 \
  -v $(pwd)/results:/app/OneForAll/results \
  ghcr.io/w95/oneforall-api:latest
```

### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd oneforall
   ```

2. **Start the service**:
   ```bash
   docker-compose up -d
   ```

3. **The API will be available at**: `http://localhost:9403`

### Manual Installation

1. **Install Python dependencies**:
   ```bash
   pip3.10 install -r requirements.txt
   ```

2. **Install OneForAll**:
   ```bash
   # Download and setup OneForAll in /app/OneForAll/
   # Follow OneForAll installation instructions
   ```

3. **Run the API**:
   ```bash
   python3.10 main.py
   ```

## API Documentation

### Endpoints

#### `POST /scan`

Perform a subdomain scan on a target domain.

**Parameters:**
- `url` (string, required): Target domain to scan
- `http_requests` (boolean, optional): Enable HTTP requests during scan (default: `false`)
- `check_alive` (boolean, optional): Only export alive subdomains (default: `false`)

**Example Request:**
```bash
curl -X POST "http://localhost:9403/scan" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "url=example.com&http_requests=true&check_alive=true"
```

**Example Response:**
```json
{
  "results": [
    {
      "subdomain": "www.example.com",
      "ip": "93.184.216.34",
      "status": "alive",
      "title": "Example Domain"
    }
  ],
  "target": "example.com",
  "total_count": 1
}
```

#### `GET /`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### Interactive API Documentation

Once the service is running, you can access:
- **Swagger UI**: `http://localhost:9403/docs`
- **ReDoc**: `http://localhost:9403/redoc`

## Configuration

### Environment Variables

- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered (useful for Docker logs)

### OneForAll Configuration

The service uses OneForAll with the following default parameters:
- `--fmt json`: Output format set to JSON
- `--req True/False`: HTTP requests enabled/disabled based on parameter
- `--alive True`: Only alive subdomains (when `check_alive=true`)

## Docker Images

### Available Images

The OneForAll API is available as pre-built Docker images:

- **GitHub Container Registry**: `ghcr.io/w95/oneforall-api:latest`
- **Tags Available**:
  - `latest` - Latest stable release
  - `main` - Latest development build
  - `v1.0.0` - Specific version tags

### Image Details

- **Base Image**: `python:3.10-alpine`
- **Size**: ~500MB (includes OneForAll + MassDNS)
- **Architecture**: `linux/amd64`, `linux/arm64`
- **Automatic Updates**: Images are automatically built on new releases

### Using Different Tags

```bash
# Use latest stable
docker pull ghcr.io/w95/oneforall-api:latest

# Use development version
docker pull ghcr.io/w95/oneforall-api:main

# Use specific version
docker pull ghcr.io/w95/oneforall-api:v1.0.0
```

## Docker Configuration

### Dockerfile Features

- **Base Image**: `python:3.10-alpine` for minimal footprint
- **OneForAll Integration**: Automatically downloads and configures OneForAll
- **MassDNS**: Builds and integrates MassDNS for DNS resolution
- **Volume Mounting**: Results directory mounted for persistence

### Docker Compose

```yaml
services:
  oneforall-api:
    build: .
    volumes:
      - ./results:/app/OneForAll/results
    ports:
      - "9403:9403"
    environment:
      - PYTHONUNBUFFERED=1
```

## Results Storage

Scan results are stored in the `results/` directory:
- JSON files: `{domain}.json`
- Logs: `oneforall.log`, `massdns.log`
- Temporary files: `temp/` subdirectory

## Error Handling

The API includes comprehensive error handling for:
- Invalid domains
- OneForAll execution failures
- Timeout scenarios (5-minute limit)
- Missing result files
- JSON parsing errors

## Logging

Detailed logging is provided for:
- Scan initiation and completion
- Command execution details
- File system operations
- Error conditions

## Development

### Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- OneForAll dependencies

### Local Development

1. **Install dependencies**:
   ```bash
   pip3.10 install -r requirements.txt
   ```

2. **Run in development mode**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 9403
   ```

## Security Considerations

- The API runs on port 9403 by default
- Input validation is performed on domain names
- Timeout protection prevents resource exhaustion
- Consider implementing authentication for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the same terms as OneForAll. Please refer to the OneForAll repository for license details.

## Acknowledgments

- [OneForAll](https://github.com/shmilylty/OneForAll) - The core subdomain enumeration tool
- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [MassDNS](https://github.com/blechschmidt/massdns) - DNS resolution tool

## Support

For issues and questions:
1. Check the logs in the `results/` directory
2. Review the OneForAll documentation
3. Open an issue in this repository

---

**Note**: This is a wrapper service for OneForAll. For detailed information about subdomain enumeration techniques and OneForAll-specific features, please refer to the [official OneForAll documentation](https://github.com/shmilylty/OneForAll).

# ViciDial AI Voice Integration

This project integrates AI voice capabilities (Retell AI/Vapi) with ViciDial to create an automated outbound calling system.

## System Architecture

The integration consists of several key components:

1. **ViciDial Client**: Handles interaction with ViciDial's API for lead management and call control
2. **AI Voice Client**: Manages communication with AI voice services (Retell/Vapi)
3. **Integration Middleware**: Coordinates between ViciDial and AI voice services
4. **Database Handler**: Manages call records and campaign data
5. **Campaign Scheduler**: Automates campaign execution based on configured schedules

## Prerequisites

- Python 3.8+
- ViciDial server with API access
- AI Voice service account (Retell or Vapi)
- SQLite3
- Linux server with minimum 4GB RAM, 2 CPU cores

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Edit the `.env` file with your specific settings:

- ViciDial credentials and server URL
- AI Voice service API key and service type
- Webhook configuration
- Campaign settings

## Running the System

1. Start the integration middleware (handles webhooks):
```bash
python integration_middleware.py
```

2. Start the campaign scheduler:
```bash
python scheduler.py
```

## ViciDial Configuration

1. Create custom statuses in ViciDial admin panel:
   - AICALL: Call in progress by AI
   - AICOMPL: Call completed by AI
   - AINOANS: No answer (AI call failed)

2. Configure API access for the middleware user

## Monitoring and Maintenance

The system logs important events and errors to help with monitoring and troubleshooting:

- Check application logs for detailed operation information
- Monitor the health endpoint: `GET /health`
- Review campaign statistics in the database

## Performance Optimization

Track key metrics for optimization:

- Call connection rate
- Average call duration
- Conversion rates
- AI failure rates
- Compare AI vs human agent performance

## Security Considerations

- Keep API keys and credentials secure
- Use HTTPS for webhooks
- Regularly update dependencies
- Monitor system access and usage

## Support

For issues and support:
1. Check the logs for error messages
2. Verify configuration settings
3. Ensure all services are running
4. Check network connectivity

## License

This project is licensed under the MIT License - see the LICENSE file for details.
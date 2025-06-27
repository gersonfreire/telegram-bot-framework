I'll perform an analysis of the `util_imap.py` script and create a requirements document through reverse engineering. Let me first examine the code in detail. Based on my analysis of the util_imap.py script, I'll now create a detailed requirements document through reverse engineering.

# Requirements Document: Email Alarm Monitoring System

## 1. Introduction

### 1.1 Purpose

This document specifies the requirements for an email-based alarm monitoring system that connects to IMAP servers, retrieves emails with specified subjects, extracts alarm data from HTML tables in these emails, and processes the alarm information for further use.

### 1.2 Scope

The system is designed to retrieve and parse email notifications containing alarm data, particularly from monitoring systems like Sitrad and SmartMonit. It should support multiple email providers and handle different email formats.

### 1.3 Intended Audience

This document is intended for developers who will implement or maintain the Email Alarm Monitoring System.

## 2. System Overview

The system connects to email servers via IMAP protocol, searches for unread emails with specific subjects related to alarms, extracts alarm data from HTML tables within these emails, filters the alarms based on configurable criteria, and formats the alarm information for output.

## 3. Functional Requirements

### 3.1 Email Connection Management

#### 3.1.1 IMAP Server Connection

- **FR-1.1:** The system shall establish secure connections to IMAP servers using SSL.
- **FR-1.2:** The system shall support authentication with username and password.
- **FR-1.3:** The system shall handle connection errors gracefully and provide appropriate error messages.

#### 3.1.2 Email Provider Detection

- **FR-1.4:** The system shall maintain a dictionary of common email providers and their IMAP server addresses.
- **FR-1.5:** The system shall extract domain information from email addresses to determine the appropriate IMAP server.
- **FR-1.6:** The system shall support automatic detection of IMAP servers using DNS MX record lookup.
- **FR-1.7:** The system shall provide a mechanism to detect IMAP server settings via online API.

### 3.2 Email Retrieval

#### 3.2.1 Email Filtering

- **FR-2.1:** The system shall search for unread emails in specified folders.
- **FR-2.2:** The system shall filter emails by subject.
- **FR-2.3:** The system shall limit the number of emails retrieved to a configurable maximum.

#### 3.2.2 Message Processing

- **FR-2.4:** The system shall parse email messages according to RFC822 standards.
- **FR-2.5:** The system shall handle both plain text and HTML email formats.
- **FR-2.6:** The system shall properly decode email content with appropriate character encoding.

### 3.3 Alarm Data Extraction

#### 3.3.1 HTML Parsing

- **FR-3.1:** The system shall extract HTML content from email messages.
- **FR-3.2:** The system shall parse HTML tables using BeautifulSoup or equivalent HTML parsing libraries.
- **FR-3.3:** The system shall handle different HTML table structures.

#### 3.3.2 Table Data Processing

- **FR-3.4:** The system shall extract both header and data rows from HTML tables.
- **FR-3.5:** The system shall support two different methods of HTML parsing for different email formats.
- **FR-3.6:** The system shall handle special HTML elements like `<br>` tags in the content.

### 3.4 Alarm Filtering and Formatting

#### 3.4.1 Alarm Filtering

- **FR-4.1:** The system shall filter alarms based on configurable criteria.
- **FR-4.2:** The system shall support excluding alarms containing specified text patterns.

#### 3.4.2 Text Formatting

- **FR-4.3:** The system shall format alarm data into human-readable text.
- **FR-4.4:** The system shall concatenate alarm columns with appropriate delimiters.

## 4. Non-Functional Requirements

### 4.1 Performance

- **NFR-1.1:** The system shall process emails efficiently, minimizing connection time to IMAP servers.
- **NFR-1.2:** The system shall handle multiple alarm messages in a single email.

### 4.2 Security

- **NFR-2.1:** The system shall use secure connections (SSL/TLS) to connect to email servers.
- **NFR-2.2:** The system shall not store email credentials in plaintext in the code.
- **NFR-2.3:** The system shall handle sensitive information securely.

### 4.3 Reliability

- **NFR-3.1:** The system shall handle various error conditions gracefully.
- **NFR-3.2:** The system shall provide detailed logging information for troubleshooting.

### 4.4 Maintainability

- **NFR-4.1:** The system shall follow object-oriented design principles.
- **NFR-4.2:** The system shall include comprehensive documentation in the code.
- **NFR-4.3:** The system shall handle exceptions consistently.

### 4.5 Compatibility

- **NFR-5.1:** The system shall support various email providers (Gmail, Outlook, Yahoo, etc.).
- **NFR-5.2:** The system shall handle different character encodings, particularly UTF-8 and ISO-8859-1.

## 5. External Interface Requirements

### 5.1 User Interfaces

- No direct user interface is required as the system is primarily a backend service.

### 5.2 Hardware Interfaces

- No special hardware requirements.

### 5.3 Software Interfaces

- **SIR-1:** The system shall integrate with Python's imaplib for IMAP connections.
- **SIR-2:** The system shall use BeautifulSoup for HTML parsing.
- **SIR-3:** The system shall utilize DNS resolver for MX record lookups.

### 5.4 Communication Interfaces

- **CIR-1:** The system shall use IMAP protocol over SSL/TLS.
- **CIR-2:** The system shall support HTTP requests for IMAP server detection via external API.

## 6. Configuration Requirements

### 6.1 Email Configuration

- **CR-1.1:** The system shall read IMAP server settings from a configuration file.
- **CR-1.2:** The system shall support configurable email subjects for filtering.
- **CR-1.3:** The system shall allow configuration of the target email folder.

### 6.2 Alarm Processing Configuration

- **CR-2.1:** The system shall support configurable alarm filters.
- **CR-2.2:** The system shall support different email layouts (Sitrad and others).

## 7. Data Requirements

### 7.1 Data Storage

- No persistent storage requirements are identified in the current implementation.

### 7.2 Data Format

- **DR-1:** The system shall handle HTML data within emails.
- **DR-2:** The system shall process tabular data in HTML format.
- **DR-3:** The system shall output alarm data in plaintext format.

## 8. Error Handling Requirements

### 8.1 Connection Errors

- **EHR-1.1:** The system shall detect and report IMAP connection failures.
- **EHR-1.2:** The system shall handle authentication failures gracefully.

### 8.2 Parsing Errors

- **EHR-2.1:** The system shall handle malformed HTML content.
- **EHR-2.2:** The system shall provide fallback mechanisms when HTML parsing fails.

### 8.3 Logging

- **EHR-3.1:** The system shall log all errors with appropriate context.
- **EHR-3.2:** The system shall provide debug-level logging for troubleshooting.

## 9. Appendices

### 9.1 Supported Email Providers

The system includes built-in support for the following email providers:

- Gmail
- Hotmail/Outlook
- Yahoo
- Terra
- UOL
- Globo.com
- IG
- BRTurbo
- Zoho
- Locaweb

### 9.2 External Resources

- Email RFC standards
- IMAP protocol documentation
- BeautifulSoup documentation
- DNS resolver documentation

## 10. Glossary

- **IMAP**: Internet Message Access Protocol
- **SSL**: Secure Sockets Layer
- **TLS**: Transport Layer Security
- **HTML**: HyperText Markup Language
- **DNS**: Domain Name System
- **MX Record**: Mail Exchange Record
- **RFC**: Request for Comments (internet standards documents)
- **BeautifulSoup**: A Python library for parsing HTML and XML documents
- **SMTP**: Simple Mail Transfer Protocol
- **POP**: Post Office Protocol
- **Sitrad**: A monitoring system for which this implementation is designed to process alarm emails

This requirements document provides a comprehensive outline derived from the reverse engineering of the util_imap.py script, capturing both the explicit and implicit requirements of the system.

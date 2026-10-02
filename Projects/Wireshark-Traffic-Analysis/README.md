# Wireshark Traffic Analysis

A SIEM lab where I analyzed real network traffic with Wireshark.

## What I did

I tracked different kinds of activity in captured traffic: a Teams call, web browsing, DNS requests, and secure HTTPS sessions. I identified specific events, including TLS handshakes for secure sessions, ARP traffic showing devices communicating on the network, and the DNS lookups behind a Teams call.

## Takeaways

- Everyday actions like browsing or video calls leave clear patterns in network traffic.
- Even with encryption, metadata such as IP addresses and timing still gives useful insight.
- Packet analysis is key to understanding how systems communicate and where risks can exist.

## Tools

Wireshark, SIEM lab environment

(Screenshots are left out of this repo because they show a home network's addresses.)

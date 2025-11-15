#include <SPI.h>
#include <MFRC522.h>

// Define the pins for the RC522 module
#define RST_PIN 9   // Reset pin
#define SS_PIN 10   // Slave Select (SDA) pin

// Create an instance of the MFRC522 reader
MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  // Start serial communication at 9600 baud
  Serial.begin(9600);
  while (!Serial); // Wait for serial port to connect (especially for boards like Leonardo)

  // Initialize the SPI bus
  SPI.begin();

  // Initialize the MFRC522 reader
  mfrc522.PCD_Init();

  Serial.println("RC522 Reader Ready");
  Serial.println("Scan an NFC/RFID tag...");
}

void loop() {
  // Look for new cards (tags)
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return; // If no card is present, exit the loop and try again
  }

  // Select one of the cards
  if (!mfrc522.PICC_ReadCardSerial()) {
    return; // If reading the card fails, exit the loop
  }

  // If we are here, a card was successfully read
  Serial.print("Card UID: ");
  printUID(mfrc522.uid.uidByte, mfrc522.uid.size);
  Serial.println();

  // Halt the card to allow new cards to be read
  mfrc522.PICC_HaltA();
}

/**
 * Helper function to print the UID byte array in a readable hex format.
 */
void printUID(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    // Add a leading zero if the hex value is less than 0x10
    if (buffer[i] < 0x10) {
      Serial.print(" 0");
    } else {
      Serial.print(" ");
    }
    Serial.print(buffer[i], HEX);
  }
}
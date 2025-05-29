#include <Servo.h>

Servo elbowServo;
Servo handServo;

int elbowCurrentAngle = 90;  // Start elbow at neutral position
int handCurrentAngle = 80;   // Start hand at open position (adjust as needed)

// Use constants for hand open/close angles for clarity and easy tuning
const int HAND_OPEN_ANGLE = 80;
const int HAND_CLOSE_ANGLE = 10;

void setup() {
  Serial.begin(9600);

  // Hold servo signal pins LOW before attaching servos to avoid jitter
  pinMode(9, OUTPUT);
  digitalWrite(9, LOW);
  delay(500);
  elbowServo.attach(9);

  pinMode(10, OUTPUT);
  digitalWrite(10, LOW);
  delay(500);
  handServo.attach(10);

  // Move servos to initial safe positions and allow time to stabilize
  elbowServo.write(elbowCurrentAngle);
  handServo.write(handCurrentAngle);
  delay(1500);  // Increased delay to stabilize servo on startup
}

void moveElbow(int targetAngle) {
  if (elbowCurrentAngle == targetAngle) {
    Serial.println("Elbow already in target position.");
    return;
  }

  int step = (targetAngle > elbowCurrentAngle) ? 1 : -1;

  while (elbowCurrentAngle != targetAngle) {
    elbowCurrentAngle += step;
    elbowServo.write(elbowCurrentAngle);
    delay(30);  // Delay controls speed; increase to slow down movement
  }
  Serial.print("Elbow moved to: ");
  Serial.println(elbowCurrentAngle);
}

void moveHand(int targetAngle) {
  if (handCurrentAngle == targetAngle) {
    Serial.println("Hand already in target position.");
    return;
  }

  int step = (targetAngle > handCurrentAngle) ? 1 : -1; 

  while (handCurrentAngle != targetAngle) {
    handCurrentAngle += step;
    handServo.write(handCurrentAngle);
    delay(30);  // Delay controls speed; increase to slow down movement
  }
  Serial.print("Hand moved to: ");
  Serial.println(handCurrentAngle);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command == "elbow_flexion") {
      moveElbow(30);
      delay(1000);  // Hold position before next command
    }
    else if (command == "elbow_extension") {
      moveElbow(90);
      delay(1000);
    }
    else if (command == "hand_close") {
      moveHand(HAND_CLOSE_ANGLE);
      delay(1000);
    }
    else if (command == "hand_open") {
      moveHand(HAND_OPEN_ANGLE);
      delay(1000);
    }
    else {
      Serial.print("Unknown command received: ");
      Serial.println(command);
    }
  }
}

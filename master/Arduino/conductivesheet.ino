// Velostat pressure sensor - voltage divider version
const int sensorPin = A0;
const int samples = 8;        // smoothing samples
int minReading = 1023;
int maxReading = 0;

void setup() {
  Serial.begin(115200);
  pinMode(sensorPin, INPUT);

  // Auto-calibrate (quick): first leave alone, then press
  Serial.println("Calibration: keep sensor untouched for 2 seconds...");
  delay(2000);
  int base = readAverage(100);
  Serial.print("Baseline avg (no press): "); Serial.println(base);

  Serial.println("Now press sensor firmly for 2 seconds (place a weight or press hard)...");
  delay(2000);
  int peak = readAverage(100);
  Serial.print("Peak avg (pressed): "); Serial.println(peak);

  // Use them (but guard in case reversed)
  minReading = min(base, peak);
  maxReading = max(base, peak);
  if (minReading == maxReading) { // fallback
    minReading = 0;
    maxReading = 1023;
  }
  Serial.print("Calibration done. min="); Serial.print(minReading);
  Serial.print("  max="); Serial.println(maxReading);
  Serial.println("Reading values:");
}

void loop() {
  int raw = readAverage(samples);
  float voltage = raw * (5.0 / 1023.0); // if using default 5V reference
  // map to 0-100% with clamping
  float percent = 100.0 * (raw - minReading) / float(maxReading - minReading);
  if (percent < 0) percent = 0;
  if (percent > 100) percent = 100;

  Serial.print("Raw: ");
  Serial.print(raw);
  Serial.print("  V: ");
  Serial.print(voltage, 3);
  Serial.print("  %: ");
  Serial.println(percent, 1);

  delay(100); // 10 Hz
}

int readAverage(int n) {
  long sum = 0;
  for (int i = 0; i < n; i++) {
    sum += analogRead(sensorPin);
    delay(2);
  }
  return int(sum / n);
}

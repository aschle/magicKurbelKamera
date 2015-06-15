#include <ClickButton.h> // https://code.google.com/p/clickbutton/
#include <Encoder.h>

Encoder encoder(2, 3);
ClickButton rec_button(4, LOW, CLICKBTN_PULLUP);
ClickButton abort_button(7, LOW, CLICKBTN_PULLUP);
int rec_button_state = 0;
int abort_button_state = 0;

void setup() {
  Serial.begin(9600);
  Keyboard.begin();

  rec_button.debounceTime   = 20;   // Debounce timer in ms
  rec_button.multiclickTime = 250;  // Time limit for multi clicks
  rec_button.longClickTime  = 2500; // time until "held-down clicks" register

  abort_button.debounceTime   = 20;   // Debounce timer in ms
  abort_button.multiclickTime = 250;  // Time limit for multi clicks
  abort_button.longClickTime  = 2500; // time until "held-down clicks" register
}

long pos  = -999;
long last_value = 0;
long act_value = 0;

int distance = 10; // how many ticks until keypress is fired, 10 seemed to result in ~8 keys per round

void loop() {

  long newPos = encoder.read();
  if(newPos > pos)     { act_value += 1; }
  else if(newPos < pos){ act_value -= 1; }
  if (newPos != pos)   { pos = newPos;   }

  if(act_value - last_value >= distance){ // clockwise
    Keyboard.press(KEY_RIGHT_ARROW);
    Keyboard.release(KEY_RIGHT_ARROW);
    last_value = act_value;
  } else if(act_value - last_value <= -1 * distance){ // counter clockwise
    Keyboard.press(KEY_LEFT_ARROW);
    Keyboard.release(KEY_LEFT_ARROW);
    last_value = act_value;
  }


  rec_button.Update();
  rec_button_state = rec_button.clicks;
  if(rec_button_state == 1){ // single click
    Keyboard.press('r');
    Keyboard.release('r');
  }

  abort_button.Update();
  abort_button_state = abort_button.clicks;
  if(abort_button_state == 1){ // single click
    Keyboard.press('e');
    Keyboard.release('e');
  }


//  else if(button_state == 2){ // double click
//    Keyboard.press('p');
//    Keyboard.release('p');
//  }else if(button_state == -1){ // long press
//    Keyboard.press(KEY_ESC);
//    Keyboard.release(KEY_ESC);
//  }
}

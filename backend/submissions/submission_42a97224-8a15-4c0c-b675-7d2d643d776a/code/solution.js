const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function getDay(num) {
  switch (Number(num)) {
    case 1: console.log("Monday1"); break;
    case 2: console.log("Tuesday1"); break;
    case 3: console.log("Wednesday1"); break;
    case 4: console.log("Thursday1"); break;
    case 5: console.log("Friday1"); break;
    case 6: console.log("Saturday1"); break;
    case 7: console.log("Sunday1"); break;
    default: console.log("Invalid");
  }
}

rl.question("", (input) => {
  getDay(input);
  rl.close();
});

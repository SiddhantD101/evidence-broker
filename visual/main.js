const steps = [
  {
    status: "Credential scoped",
    packet: "9%",
    color: "#326ebd",
    active: "agent",
    agent: "Calls list_credentials and sees DEMO_TOKEN plus host and method scope.",
    broker: "Returns names and policy only. The secret value remains inside the host process.",
    operator: "No approval is requested for discovery.",
    target: "No network call is made.",
    decision: `{
  "credential": "DEMO_TOKEN",
  "allowedHosts": ["127.0.0.1"],
  "allowedMethods": ["GET"],
  "value": "[never returned]"
}`,
    agentBox: `list_credentials -> DEMO_TOKEN
scope: GET http://127.0.0.1
secret: unavailable`,
    ledger: [
      ["#1", "credential-listed", "hash=932af0 prev=genesis"],
    ],
  },
  {
    status: "Default denied",
    packet: "31%",
    color: "#b34545",
    active: "broker",
    agent: "Requests DEMO_TOKEN for https://127.0.0.1.evil.test.",
    broker: "Parses the host and refuses the substring near-miss.",
    operator: "Not interrupted because policy already denies the call.",
    target: "Receives nothing.",
    decision: `{
  "granted": false,
  "code": "host-not-allowed",
  "host": "127.0.0.1.evil.test"
}`,
    agentBox: `request_credential_use -> denied
reason: host-not-allowed
secret: still unavailable`,
    ledger: [
      ["#1", "credential-listed", "hash=932af0 prev=genesis"],
      ["#2", "credential-denied", "hash=ab19c2 prev=932af0"],
    ],
  },
  {
    status: "Waiting on human",
    packet: "53%",
    color: "#a36b10",
    active: "operator",
    agent: "Requests DEMO_TOKEN for the approved loopback target.",
    broker: "Computes an action digest over credential, method, host, path, headers, and body hash.",
    operator: "Sees a pending file decision and approves exactly that action.",
    target: "Still waiting.",
    decision: `{
  "pending": true,
  "id": "req_42",
  "digest": "sha256:778ec0..."
}`,
    agentBox: `request_credential_use -> pending
grant: not issued until approval`,
    ledger: [
      ["#1", "credential-listed", "hash=932af0 prev=genesis"],
      ["#2", "credential-denied", "hash=ab19c2 prev=932af0"],
      ["#3", "approval-requested", "hash=cd4120 prev=ab19c2"],
    ],
  },
  {
    status: "Redacted response",
    packet: "76%",
    color: "#2f7d57",
    active: "target",
    agent: "Calls send with only the grant id.",
    broker: "Reads the secret, injects it once, redacts returned encodings, and seals the result.",
    operator: "Can verify the ledger after the call.",
    target: "Receives Authorization: Bearer sk-live-demo-...",
    decision: `{
  "sent": true,
  "status": 200,
  "responseHash": "sha256:1fd66b..."
}`,
    agentBox: `HTTP/200
x-echo-auth: Bearer [redacted:DEMO_TOKEN]
body: {"youSentMe":"Bearer [redacted:DEMO_TOKEN]"}`,
    ledger: [
      ["#1", "credential-listed", "hash=932af0 prev=genesis"],
      ["#2", "credential-denied", "hash=ab19c2 prev=932af0"],
      ["#3", "approval-requested", "hash=cd4120 prev=ab19c2"],
      ["#4", "credential-sent", "hash=11eed8 prev=cd4120"],
    ],
  },
  {
    status: "Replay blocked",
    packet: "44%",
    color: "#b34545",
    active: "broker",
    agent: "Tries to reuse the same grant id.",
    broker: "Rejects it because each-use grants are spent after one send.",
    operator: "No new approval exists.",
    target: "Receives no second request.",
    decision: `{
  "sent": false,
  "code": "approval-spent"
}`,
    agentBox: `send(grantId) -> denied
target contact count: 1`,
    ledger: [
      ["#1", "credential-listed", "hash=932af0 prev=genesis"],
      ["#2", "credential-denied", "hash=ab19c2 prev=932af0"],
      ["#3", "approval-requested", "hash=cd4120 prev=ab19c2"],
      ["#4", "credential-sent", "hash=11eed8 prev=cd4120"],
      ["#5", "send-denied", "hash=e2814c prev=11eed8"],
    ],
  },
  {
    status: "Chain verified",
    packet: "92%",
    color: "#2f7d57",
    active: "operator",
    agent: "Can ask for recent evidence but cannot edit or approve it.",
    broker: "Recomputes each row hash and compares the tail against the stored head.",
    operator: "Runs verify and gets a precise failure point if a row was edited.",
    target: "Outside the verification path.",
    decision: `{
  "ok": true,
  "count": 5,
  "headHash": "e2814c..."
}`,
    agentBox: `verify_evidence -> ok
tamper check: passed`,
    ledger: [
      ["#1", "credential-listed", "hash=932af0 prev=genesis"],
      ["#2", "credential-denied", "hash=ab19c2 prev=932af0"],
      ["#3", "approval-requested", "hash=cd4120 prev=ab19c2"],
      ["#4", "credential-sent", "hash=11eed8 prev=cd4120"],
      ["#5", "send-denied", "hash=e2814c prev=11eed8"],
    ],
  },
];

const actors = [...document.querySelectorAll(".actor")];
const buttons = [...document.querySelectorAll(".step-button")];
const packet = document.querySelector("#packet");
const statusPill = document.querySelector("#statusPill");
const fields = {
  agent: document.querySelector("#agentText"),
  broker: document.querySelector("#brokerText"),
  operator: document.querySelector("#operatorText"),
  target: document.querySelector("#targetText"),
  decision: document.querySelector("#decisionBox"),
  agentBox: document.querySelector("#agentBox"),
  ledger: document.querySelector("#ledgerRows"),
};

function tagFor(kind) {
  if (kind.includes("denied")) return "deny";
  if (kind.includes("sent")) return "allow";
  return "info";
}

function render(index) {
  const step = steps[index];
  statusPill.textContent = step.status;
  packet.style.left = step.packet;
  packet.style.background = step.color;

  fields.agent.textContent = step.agent;
  fields.broker.textContent = step.broker;
  fields.operator.textContent = step.operator;
  fields.target.textContent = step.target;
  fields.decision.textContent = step.decision;
  fields.agentBox.textContent = step.agentBox;
  fields.ledger.innerHTML = step.ledger
    .map(
      ([seq, kind, hash]) => `
        <div class="ledger-row">
          <strong>${seq}</strong>
          <span class="tag ${tagFor(kind)}">${kind}</span>
          <span>${hash}</span>
        </div>`,
    )
    .join("");

  buttons.forEach((button, buttonIndex) => {
    button.classList.toggle("active", buttonIndex === index);
  });
  actors.forEach((actor) => actor.classList.toggle("active", actor.classList.contains(step.active)));
}

buttons.forEach((button) => {
  button.addEventListener("click", () => render(Number(button.dataset.step)));
});

render(0);

Absolutely! Here's the **full and clean Markdown version** of your content, fully unbroken, ready to paste into `README.md`:

---

```markdown
# 🛠️ SRE FETCH Take Home Assignment – Endpoint Health Monitor

---

## 📌 Overview

This project is a health monitoring script that evaluates the availability of HTTP endpoints based on configuration from a YAML file. It performs checks every 15 seconds and logs the availability percentage for each domain. The system is designed to handle malformed inputs gracefully and focuses on correctness, performance, and clarity.

---

## 📥 Installation

### ✅ Prerequisites
- Python 3.6 or higher

### ✅ Required Libraries

This project uses the following third-party packages:

- `pyyaml` – For parsing the YAML configuration file
- `requests` – For sending HTTP/HTTPS requests to endpoints

### ✅ Install Using pip

```bash
pip install pyyaml requests
```

---

## 🐞 Issue 1: Missing HTTP Method in Input

**Problem:**  
Initially, the script would throw an exception if one of the endpoints did not include the `method` field (it was `None`).

**Fix:**  
```python
method = endpoint.get('method', 'GET')
```

This sets a default value of `"GET"` for any endpoint missing the `method` field, as required by the assignment.

---

## 🧩 Issue 2: Domain Grouping Without Port

**Problem:**  
The original code:

```python
endpoint["url"].split("//")[-1].split("/")[0]
```

would include the port in the domain grouping if a port was present (e.g., `example.com:8080`).

**Fix:**  
Updated the code to exclude the port:

```python
domainUrl = endpoint["url"].split("//")[-1].split("/")[0]
domain = domainUrl.split(":")[0]
```

**Tested:**  
Validated by including URLs with ports, and confirmed it grouped by the domain only.

---

## 🚦 Feature 1: Response Time Check (< 500ms)

**What I did:**  
Added a check to consider an endpoint **DOWN** if it responds in over 500 milliseconds, even if the status code is 2xx.

**Code Change:**

```python
startReqTime = time.time()
response = requests.request(method, url, headers=headers, json=body)
timeTaken = (time.time() - startReqTime) * 1000

if 200 <= response.status_code < 300 and timeTaken < 500:
    return "UP"
```

**Why:**  
To meet the SLA requirement where endpoints must respond quickly to be considered available.

---

## 🔁 Feature 2: Stats Reset Every Cycle

**Problem:**  
Stats were previously declared outside the loop, so counts accumulated across cycles — leading to incorrect availability percentages.

**Fix:**  
Moved stats reset inside the `while True` loop:

```python
while True:
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
```

**Result:**  
Each 15-second cycle starts fresh, showing accurate availability for that cycle.

---

## 🔐 Feature 3: Input Validation

**What I did:**  
Added checks to skip endpoints missing required fields (`url`, `name`) or where those fields are empty.

**Code Snippet:**

```python
if "url" not in endpoint or not endpoint["url"]:
    logging.warning(f"Skipping endpoint: missing or empty 'url' → {endpoint}")
    continue
if "name" not in endpoint or not endpoint["name"]:
    logging.warning(f"Skipping endpoint: missing or empty 'name' → {endpoint}")
    continue
```

---

## 🧾 Feature 4: Per-Endpoint Health Logging

**Problem:**  
The original code only logged domain-level availability. It was hard to trace individual endpoint health.

**Fix:**  
Added logging per endpoint:

```python
logging.info(f"The result of the endpoint '{endpoint['name']}' ({endpoint['url']}) is [{result}]")
```

**Result:**  
Every endpoint’s status is clearly logged each cycle.

---

## ✨ Enhancements

### 🔹 Enhancement 1: Replaced `print()` with Structured Logging

**Code Change:**

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
```

- Replaced all `print()` calls with `logging`.
- Logs now include timestamps and log levels.
- Output is structured for compatibility with observability tools like **Loki**, **New Relic**, or any **time-series DB**.
- Improves traceability, production readiness, and long-term monitoring support.

---

### 🔹 Enhancement 2: Logged Slow-but-Successful Requests

**Code Snippet:**

```python
if 200 <= response.status_code < 300 and timeTaken > 500:
    logging.warning(f"Request 200 but took more than 500ms for {url}")
    return "DOWN"
if 200 <= response.status_code < 300:
    return "UP"
else:
    return "DOWN"
```

**Why:**  
To make sure slow responses (even with 200 OK) are treated as `DOWN` and are visibly flagged for performance debugging.

**Benefit:**  
Improves observability and helps track degrading backend performance over time.

---

Let me know if you'd like a matching `sample.yaml`, `test cases`, or markdown to PDF export!
```
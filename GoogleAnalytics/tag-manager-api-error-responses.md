Error Responses

bookmark_border

Standard Error Responses
If a Tag Manager API request is successful, the API returns a 200 HTTP status code along with the requested data in the body of the response.

If an error occurs with a request, the API returns an HTTP status code and reason in the response based on the type of error. Additionally, the body of the response contains a detailed description of what caused the error. Here's an example of an error response:


400 invalidParameter

{
 "error": {
  "errors": [
   {
    "domain": "usageLimits",
    "reason": "accessNotConfigured",
    "message": "Access Not Configured. Please use Google Developers Console to activate the API for your project.",
   }
  ],
  "code": 403,
  "message": "Access Not Configured. Please use Google Developers Console to activate the API for your project."
 }
}
Note: The description could change at any time so applications should not depend on the actual description text.

Implementing Exponential Backoff
Exponential backoff is the process of a client periodically retrying a failed request over an increasing amount of time. It is a standard error handling strategy for network applications. The Tag Manager API is designed with the expectation that clients which choose to retry failed requests do so using exponential backoff. Besides being "required", using exponential backoff increases the efficiency of bandwidth usage, reduces the number of requests required to get a successful response, and maximizes the throughput of requests in concurrent environments.

The flow for implementing simple exponential backoff is as follows.

Make a request to the API.
Receive an error response that has an error code that can be retried.
Wait 1 second + random_number_milliseconds seconds.
Retry request.
Receive an error response that has an error code that can be retried.
Wait 2 seconds + random_number_milliseconds seconds.
Retry request.
Receive an error response that has an error code that can be retried.
Wait 4 seconds + random_number_milliseconds seconds.
Retry request.
Receive an error response that has an error code that can be retried.
Wait 8 seconds + random_number_milliseconds seconds.
Retry request.
Receive an error response that has an error code that can be retried.
Wait 16 seconds + random_number_milliseconds seconds.
Retry request.
If you still get an error, stop and log the error.
In the above flow, random_number_milliseconds is a random number of milliseconds less than or equal to 1,000. This is necessary to avoid certain lock errors in some concurrent implementations. random_number_milliseconds must be redefined after each wait.

Note: The wait is always (2 ^ n) + random_number_milliseconds, where n is a monotonically increasing integer initially defined as 0. The variable n is incremented by 1 for each iteration (each request).

The algorithm is set to terminate when n is 5. This ceiling is in place only to stop clients from retrying infinitely, and results in a total delay of around 32 seconds before a request is deemed "an unrecoverable error."

The following Python code is an implementation of the above flow for recovering from errors that occur in a method called makeRequest.


import random
import time
from apiclient.errors import HttpError

def makeRequestWithExponentialBackoff(tagmanager):
  """Wrapper to request Google Tag Manager data with exponential backoff.

  The makeRequest method accepts the tagmanager service object, makes API
  requests and returns the response. If any error occurs, the makeRequest
  method is retried using exponential backoff.

  Args:
    tagmanager: The tagmanager service object

  Returns:
    The API response from the makeRequest method.
  """
  for n in range(0, 5):
    try:
      return makeRequest(tagmanager)

    except HttpError, error:
      if error.resp.reason in ['userRateLimitExceeded', 'quotaExceeded']:
        time.sleep((2 ** n) + random.random())

  print "There has been an error, the request never succeeded."
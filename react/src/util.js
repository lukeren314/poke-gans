export async function getRequest(root, params, notify) {
  try {
    let response = await fetch(getRequestUrl(root, params), {
      credentials: "omit",
    });
    var [json, statusCode] = await response.json();
  } catch (err) {
    notify(`Bad Request: Try again`, "error");
  }
  if (statusCode !== 200) {
    console.log(`server status code: ${statusCode}`);
  }

  if (json) {
    if ("invalid" in json) {
      notify(`Invalid Request: ${json["invalid"]}`, "error");
    } else if ("error" in json) {
      notify(`Server Error: ${json["error"]}`, "error");
    } else {
      return json;
    }
  } else {
    notify(`Missing Server Data: Try Again`, "error");
  }
}

function getRequestUrl(root, params) {
  return (
    `/${root}?` +
    Object.keys(params)
      .map((key) => `${key}=${params[key]}`)
      .join("&")
  );
}

export function getMonsterSrc(monster) {
  return `/images/${monster.id}`;
}

export default { getRequest, getMonsterSrc };

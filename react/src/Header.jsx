import React from "react";
import "./Header.css";

function Header(props) {
  return (
    <header>
      <div className="menu-bar">
        <div className="title">
          <img
            src={process.env.PUBLIC_URL + "/titlelogo.png"}
            className="header-logo"
            alt={process.env.PUBLIC_URL + "/titlelogo.png"}
          />
        </div>
        {props.loggedIn ? (
          <div className="account">
            <p className="username">{props.username}</p>
            <button className="logout-button" onClick={props.logout}>
              Log Out
            </button>
          </div>
        ) : null}
      </div>
    </header>
  );
}
export default Header;

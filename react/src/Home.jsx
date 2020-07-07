import React from "react";
import "./Home.css";

import { getMonsterSrc } from "./util";

class Home extends React.Component {
  constructor(props) {
    super(props);
    this.state = { codes: "", clipboardCodes: "", copySuccess: null };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleClipBoardChange = this.handleClipBoardChange.bind(this);
    this.copyCodes = this.copyCodes.bind(this);
  }
  handleChange(event) {
    this.setState({ codes: event.target.value });
  }
  handleSubmit(event) {
    event.preventDefault();
    this.props.submitCodes(this.state.codes);
  }
  handleClipBoardChange(event) {
    this.setState({ clipboardCodes: event.target.value });
  }
  copyCodes(event) {
    this.codesRef.select();
    document.execCommand("copy");
    event.target.focus();
    this.props.notify("Copied!", "normal");
  }
  render() {
    return (
      <div className="Home">
        <div className="home-left">
          <div className="codes-form">
            <h1 className="user-codes-title">Your Codes</h1>
            <textarea
              className="user-codes"
              ref={(codes) => (this.codesRef = codes)}
              value={this.props.monsters
                .map((monster) => monster.code)
                .join("\n")}
              onChange={this.handleClipBoardChange}
              readOnly
            ></textarea>

            <button className="copy-codes" onClick={this.copyCodes}>
              Copy Your Monster Codes to Clipboard
            </button>
            <form className="enter-codes-form" onSubmit={this.handleSubmit}>
              <label className="enter-codes">Enter Monster Codes:</label>
              <input
                className="enter-codes-input"
                type="text"
                value={this.state.codes}
                onChange={this.handleChange}
              />
              <button className="submit-codes" type="submit">
                Submit Codes
              </button>
            </form>

            <div className="codes-log">
              <div className="codes-log-title">Code Log:</div>
              <textarea
                readOnly
                className="codes-log-text"
                value={
                  this.props.codesLog && this.props.codesLog.length > 0
                    ? this.props.codesLog.join("\n")
                    : "Submit monster code(s) separated by spaces above!"
                }
              ></textarea>
            </div>
          </div>
        </div>
        <div className="home-right">
          {this.props.dailyMonster ? (
            <div className="daily-monster">
              <h1 className="daily-monster-title">Daily Monster</h1>
              <img
                className="daily-monster-image"
                src={getMonsterSrc(this.props.dailyMonster)}
                alt={this.props.dailyMonster.name}
              />
              <div className="daily-monster-info">
                <p className="daily-monster-name">
                  {this.props.dailyMonster.name}
                </p>
                <p className="daily-monster-code">
                  Code: {this.props.dailyMonster.code}
                </p>
              </div>
            </div>
          ) : (
            <p>Daily Monster Not Found</p>
          )}
        </div>
      </div>
    );
  }
}

export default Home;

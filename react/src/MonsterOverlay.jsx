import React from "react";
import "./MonsterOverlay.css";
import { getMonsterSrc } from "./util";

class MonsterOverlay extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <div
        style={this.props.monster ? { display: "block" } : { display: "none" }}
        className="monster-overlay"
      >
        <div className="overlay-container">
          <button
            className="overlay-close-button"
            onClick={this.props.closeMonsterOverlay}
          >
            Close
          </button>
          {this.props.monster ? (
            <div>
              <div className="monster-viewer">
                <img
                  className="overlay-image"
                  src={getMonsterSrc(this.props.monster)}
                  alt={this.props.monster.name}
                />
              </div>
              <div className="overlay-info">
                <div className="overlay-name">{this.props.monster.name}</div>
                <div className="overlay-code">
                  Code: {this.props.monster.code}
                </div>
              </div>{" "}
            </div>
          ) : (
            <p>Monster Not Found</p>
          )}
        </div>
      </div>
    );
  }
}
export default MonsterOverlay;

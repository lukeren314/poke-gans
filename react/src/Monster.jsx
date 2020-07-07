import React from "react";
import "./Monster.css";
import { getMonsterSrc } from "./util";

class Monster extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hovering: false, top: 0, left: 0 };
    this.onMouseEnter = this.onMouseEnter.bind(this);
    this.onMouseMove = this.onMouseMove.bind(this);
    this.onMouseLeave = this.onMouseLeave.bind(this);
  }
  onMouseEnter(event) {
    this.setState({ hovering: true });
  }
  onMouseMove(event) {
    this.setState({ top: event.clientY, left: event.clientX });
  }
  onMouseLeave(event) {
    this.setState({ hovering: false });
  }
  render() {
    return (
      <div
        onMouseEnter={this.onMouseEnter}
        onMouseMove={this.onMouseMove}
        onMouseLeave={this.onMouseLeave}
        onClick={this.props.onClick}
        className="monster"
      >
        {this.props.monster ? (
          <div>
            <img
              className="monster-image"
              src={getMonsterSrc(this.props.monster)}
              alt={this.props.monster.name}
            />
            <div
              style={{ top: this.state.top, left: this.state.left }}
              className={this.state.hovering ? "monster-menu" : "hidden"}
            >
              <div className="info">
                <p className="overlay-name">{this.props.monster.name}</p>
                <p className="monster-code">Code: {this.props.monster.code}</p>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    );
  }
}

export default Monster;

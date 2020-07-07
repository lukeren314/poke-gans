import React from "react";
import "./Monsters.css";
import Monster from "./Monster";

class Monsters extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      menuStatus: "",
    };
    this.openMenu = this.openMenu.bind(this);
    this.closeMenu = this.closeMenu.bind(this);
  }
  openMenu() {
    this.setState({ menuStatus: "show-menu" });
  }
  closeMenu() {
    this.setState({ menuStatus: "" });
  }
  render() {
    return (
      <div className="Monsters">
        <div id="menu" className={this.state.menuStatus}>
          {this.props.monsters && (
            <div className="monsters-collected">
              Monsters Collected: {this.props.monsters.length}
            </div>
          )}
          <button className="menu-button" onClick={this.openMenu}>
            Monsters
          </button>
          <button className="close-menu" onClick={this.closeMenu}>
            Close
          </button>
          <div className="menu-container">
            <div className="monsters-container">
              {this.props.monsters
                ? this.props.monsters.map((monster) => {
                    return (
                      <div key={monster.id}>
                        <Monster
                          onClick={() => this.props.openMonsterOverlay(monster)}
                          monster={monster}
                        />
                      </div>
                    );
                  })
                : null}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Monsters;

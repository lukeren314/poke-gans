/*

ADD EMAIL, INVITE LINKS
*/

import React from "react";
import "./App.css";
import Header from "./Header";
import Footer from "./Footer";

import Login from "./Login";
import Home from "./Home";
import Monsters from "./Monsters";

import MonsterOverlay from "./MonsterOverlay";

import { getRequest } from "./util";

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loggedIn: false,
      userId: null,
      monsters: [],
      created: null,
      username: null,
      dailyMonster: null,

      codesLog: [],
      selectedMonsters: [],
      loading: false,
      notifications: [],
    };
    this.login = this.login.bind(this);
    this.register = this.register.bind(this);
    this.setUserInfo = this.setUserInfo.bind(this);
    this.startLoading = this.startLoading.bind(this);
    this.stopLoading = this.stopLoading.bind(this);

    this.logout = this.logout.bind(this);
    this.notify = this.notify.bind(this);
    this.openMonsterOverlay = this.openMonsterOverlay.bind(this);
    this.closeMonsterOverlay = this.closeMonsterOverlay.bind(this);

    this.submitCodes = this.submitCodes.bind(this);
  }
  async componentDidMount() {
    // temporary login stuff
    this.timer = setInterval(() => {
      if (this.state.notifications) {
        for (let i = this.state.notifications.length - 1; i >= 0; i--) {
          this.state.notifications[i].time--;
          if (this.state.notifications[i].time < 0) {
            this.state.notifications.splice(i, 1);
          }
        }
        this.setState({
          notifications: this.state.notifications,
        });
      }
    });
  }
  async login(username, password) {
    if (this.state.loading) {
      return;
    }
    this.startLoading();
    let json = await getRequest(
      "login",
      { username: username, password: password },
      this.notify
    );
    if (json) {
      this.setUserInfo(json);
    }
    this.stopLoading();
  }
  async register(username, password) {
    if (this.state.loading) {
      return;
    }
    this.startLoading();
    let json = await getRequest(
      "register",
      { username: username, password: password },
      this.notify
    );
    if (json) {
      this.setUserInfo(json);
      this.state.selectedMonsters.push(json.monsters[0]);
      this.setState({ selectedMonsters: this.state.selectedMonsters });
    }
    this.stopLoading();
  }
  setUserInfo(json) {
    this.setState({
      loggedIn: true,
      userId: json.id,
      username: json.username,
      created: json.created,
      monsters: json.monsters,
      dailyMonster: json.dailyMonster,
    });
  }
  async submitCodes(codes) {
    if (!codes) {
      return;
    }
    if (this.state.loading) {
      return;
    }
    this.startLoading();
    let json = await getRequest(
      "codes",
      { userId: this.state.userId, codes: codes },
      this.notify
    );
    if (json) {
      // add to the log the new monsters
      this.setUserInfo(json.user);
      this.state.selectedMonsters.push(...json.redeemed);
      this.state.codesLog.push(...json.log);
      this.setState({
        selectedMonsters: this.state.selectedMonsters,
        codesLog: this.state.codesLog,
      });
    }

    this.stopLoading();
  }
  startLoading() {
    this.setState({ loading: true });
  }
  stopLoading() {
    this.setState({ loading: false });
  }
  logout() {
    this.setState({
      loggedIn: false,
      userId: null,
      username: null,
      created: null,
      monsters: [],
      dailyMonster: null,
      selectedMonsters: [],
      codesLog: [],
    });
  }
  openMonsterOverlay(monster) {
    this.state.selectedMonsters.push(monster);
    this.setState({
      selectedMonsters: this.state.selectedMonsters,
    });
  }
  closeMonsterOverlay() {
    this.state.selectedMonsters.pop();
    this.setState({ selectedMonsters: this.state.selectedMonsters });
  }
  notify(message, type, duration = 500) {
    this.state.notifications.push({
      message: message,
      time: duration,
      type: type,
    });
    this.setState({ notifications: this.state.notifications });
    // console.log(`${message} ${type}`);
  }
  render() {
    return (
      <div>
        <Header
          monster={this.state.monsters}
          username={this.state.username}
          loggedIn={this.state.loggedIn}
          logout={this.logout}
        />
        {this.state.notifications ? (
          <div className="notifications">
            <ul className="notifications-list">
              {this.state.notifications.map((notification, i) => (
                <li className={"notification " + notification.type} key={i}>
                  {notification.message}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        {this.state.loading ? (
          <div className="loading">
            <img
              src={process.env.PUBLIC_URL + "/loading.png"}
              className="loading-image"
              alt="loading"
            />
          </div>
        ) : null}
        {this.state.selectedMonsters &&
        this.state.selectedMonsters.length > 0 ? (
          <MonsterOverlay
            monster={
              this.state.selectedMonsters[
                this.state.selectedMonsters.length - 1
              ]
            }
            closeMonsterOverlay={this.closeMonsterOverlay}
          />
        ) : null}
        {this.state.loggedIn ? (
          <Monsters
            monsters={this.state.monsters}
            openMonsterOverlay={this.openMonsterOverlay}
          />
        ) : null}
        {this.state.loggedIn ? (
          <Home
            username={this.state.username}
            monsters={this.state.monsters}
            created={this.state.created}
            codesLog={this.state.codesLog}
            submitCodes={this.submitCodes}
            dailyMonster={this.state.dailyMonster}
            notify={this.notify}
          />
        ) : (
          <Login login={this.login} register={this.register} />
        )}
        <Footer />
      </div>
    );
  }
}

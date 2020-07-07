import React from "react";
import "./Login.css";
import { TextField, Button } from "@material-ui/core";

class Login extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      saveUsername: false,
      register: false,
    };
    this.switch = this.switch.bind(this);
    this.handleUsernameChange = this.handleUsernameChange.bind(this);
    this.handlePasswordChange = this.handlePasswordChange.bind(this);
    this.handleSaveUsername = this.handleSaveUsername.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    // this.loginRef = React.createRef();
  }
  async componentDidMount() {
    if (localStorage.getItem("saveUsername")) {
      if (localStorage.getItem("username")) {
        this.setState({
          saveUsername: true,
          username: localStorage.getItem("username"),
        });
      } else {
        localStorage.setItem("saveUsername", "");
      }
    } else {
      localStorage.setItem("username", "");
    }
  }
  switch() {
    this.setState({ register: !this.state.register });
  }
  handleUsernameChange(event) {
    this.setState({ username: event.target.value });
  }
  handlePasswordChange(event) {
    this.setState({ password: event.target.value });
  }
  handleSaveUsername(event) {
    const target = event.target;
    const value =
      target.name === "saveUsername" ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value,
    });
    if (this.state.saveUsername) {
      localStorage.setItem("saveUsername", "true");
      localStorage.setItem("username", this.state.username);
    } else {
      localStorage.setItem("saveUsername", "");
      localStorage.setItem("username", "");
    }
  }
  async handleSubmit(event) {
    event.preventDefault();

    if (this.state.register) {
      this.props.register(this.state.username, this.state.password);
    } else {
      this.props.login(this.state.username, this.state.password);
    }
  }
  render() {
    return (
      <div className="Login">
        <div className="login-container">
          <h1 className="title">
            {this.state.register ? "Register" : "Login"}
          </h1>
          <form className="form" onSubmit={this.handleSubmit}>
            <div>
              <TextField
                variant="outlined"
                margin="normal"
                fullWidth
                required
                label="Username"
                value={this.state.username}
                onChange={this.handleUsernameChange}
                autoFocus
              />
              <TextField
                variant="outlined"
                margin="normal"
                fullWidth
                required
                label="Password"
                type="password"
                onChange={this.handlePasswordChange}
                // autoComplete="current-password"
              />
            </div>
            <div className="form-bottom">
              <Button
                type="submit"
                variant="contained"
                // color="#1db4fa"
                className="submit-button"
              >
                Log In
              </Button>
              {!this.state.register ? (
                <label className="save-username">
                  Save Username
                  <input
                    name="saveUsername"
                    type="checkbox"
                    checked={this.state.saveUsername}
                    onChange={this.handleSaveUsername}
                  />
                </label>
              ) : null}
            </div>
          </form>
          <div className="extra-links" onClick={this.switch}>
            {this.state.register
              ? "Login to existing account"
              : "Register an account"}
          </div>
        </div>
      </div>
    );
  }
}
export default Login;

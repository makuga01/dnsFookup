import React, { Component } from "react";
import {
  Button,
  Form,
  Grid,
  Header,
  Message,
  Segment,
  Icon,
  Statistic,
  Divider
} from "semantic-ui-react";
import {
  BrowserRouter as Router,
  Route,
  Link,
  Redirect
} from "react-router-dom";

class Dashboard extends Component {
  constructor(props) {
    super(props);
  }

  state = {
    statistics: { request_count: "?", created_bins: "?" }
  };

  getStatistics = () => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    //console.log(bearer);
    var obj = {
      method: "GET",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        //   "Access-Control-Allow-Origin": "*",
        "Access-Control-Request-Headers": "Authorization, Accept"
      })
    };
    fetch("http://localhost:5000/api/statistics", obj)
      .then(res => res.json())
      .then(data => {
        if (
          (data.msg !== "Token has expired") &
          (data.msg !== "Not enough segments")
        ) {
          this.setState({
            statistics: data
          });
        }
      })
      .catch(err => {
        console.log(err);
      });
  };
  componentDidMount() {
    this.getStatistics();
  }
  render() {
    return (
      <div>
        <Grid
          textAlign="center"
          style={{ height: "40vh" }}
          verticalAlign="middle"
        >
          <Grid.Column style={{ maxWidth: 450 }}>
            <Header size="huge" icon textAlign="center">
              <Icon name="globe" circular />
              <Header.Content>DNSfookup</Header.Content>
              <Header.Subheader>
                DNS rebinding... Just way better!
              </Header.Subheader>
            </Header>
            <Divider />
            <Statistic.Group>
              <Statistic>
                <Statistic.Value>
                  {this.state.statistics.created_bins}
                </Statistic.Value>
                <Statistic.Label>Fookup bins created</Statistic.Label>
              </Statistic>
              <Statistic>
                <Statistic.Value>
                  {this.state.statistics.request_count}
                </Statistic.Value>
                <Statistic.Label>total DNS requests recieved</Statistic.Label>
              </Statistic>
            </Statistic.Group>
            <Divider />
          </Grid.Column>
        </Grid>

        <Grid
          textAlign="center"
          style={{ height: "10vh" }}
          verticalAlign="middle"
        >
          <Grid.Column style={{ maxWidth: 650 }}>
            <Button.Group fluid vertical labeled icon>
              <Link to="/dnsbin">
                <Button size="huge" icon="globe" content="Classic DNS bin" />
              </Link>
              <Link to="/dnsbin">
                <Button
                  size="huge"
                  icon="shuffle"
                  content="Fucking overpowered DNS bin"
                />
              </Link>
            </Button.Group>
          </Grid.Column>
        </Grid>
      </div>
    );
  }
}

export default Dashboard;

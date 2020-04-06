import React, { Component } from "react";
import {
  Grid,
  Segment,
  Pagination,
  Dropdown,
  Header,
  Icon,
  Divider,
  Table,
  Menu,
  Label,
  Button,
  Popup
} from "semantic-ui-react";
import { Link } from "react-router-dom";
import {CopyToClipboard} from 'react-copy-to-clipboard';

class MyBins extends Component {
  state = {
    active: "mybins",
    selected: "",
    bins: [],
    logs: [],
    props: [],
    total_pages: 1,
    total_entries: "?",
    curr_page: 1
  };

  getBins = () => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    var obj = {
      method: "GET",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        "Access-Control-Request-Headers": "Authorization, Accept"
      })
    };
    fetch("http://rbnd.gl0.eu:5000/api/fookup/listAll", obj)
      .then(res => res.json())
      .then(data => {
        if (
          (data.msg !== "Token has expired") &
          (data.msg !== "Not enough segments")
        ) {
          this.setState({
            bins: data.reverse().map(bin => ({
              value: bin.uuid,
              text: bin.name
            }))
          });
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  getLogs = (uuid, page) => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    event.preventDefault();
    var data = {
      "uuid": uuid,
      "page": page
    };
    var obj = {
      method: "POST",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        //   "Access-Control-Allow-Origin": "*",
        'Content-Type': 'application/json',
        "Access-Control-Request-Headers": "Authorization, Accept"
      }),
      body: JSON.stringify(data)
    };
    fetch("http://rbnd.gl0.eu:5000/api/fookup/logs/uuid", obj)
      .then(res => res.json())
      .then(data => {
        if (
          (data.msg !== "Token has expired") &
          (data.msg !== "Not enough segments")
        ) {
          this.setState({
            total_pages: data.pages,
            total_entries: data.entries,
            logs: data.data.reverse()
          });
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  deleteUUID = () => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    event.preventDefault();
    var uuid = this.state.selected
    var data = {"uuid": uuid};
    var obj = {
      method: "POST",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        //   "Access-Control-Allow-Origin": "*",
        'Content-Type': 'application/json',
        "Access-Control-Request-Headers": "Authorization, Accept"
      }),
      body: JSON.stringify(data)
    };
    fetch("http://rbnd.gl0.eu:5000/api/fookup/delete", obj)
      .then(res => res.json())
      .then(data => {
        if (data.uuid_props.success === true) {
          this.setState({
            selected: ""
          });
          this.getBins();

        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  getProps = (uuid) => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    event.preventDefault();
    var data = {"uuid": uuid};
    var obj = {
      method: "POST",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        //   "Access-Control-Allow-Origin": "*",
        'Content-Type': 'application/json',
        "Access-Control-Request-Headers": "Authorization, Accept"
      }),
      body: JSON.stringify(data)
    };
    fetch("http://rbnd.gl0.eu:5000/api/fookup/props", obj)
      .then(res => res.json())
      .then(data => {
        if (data.ip_props) {
          var props = [];
          var x;
          for (x in data.ip_props){
            props.push(data.ip_props[x])
          }
          this.setState({
            'props': props
          });
          console.log(this.state.props)
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  componentDidMount() {
    this.getBins();
  }
  onChange = (e, data) => {
    this.setState(
      { selected: data.value, curr_page: 1, total_pages: 1},
    this.getLogs(data.value, 1),
    this.getProps(data.value)
    );
  };

  handleReload = () => {
    this.setState({ curr_page: 1, total_pages: 1},
      this.getLogs(this.state.selected, 1)
    );
  };

  handlePaginationChange = (e, { activePage }) => {
    this.setState({curr_page: activePage},
      this.getLogs(this.state.selected, activePage)
    );
  };



  logsTable(input_data) {
    return (
      <Table celled loading inverted>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Resolved to</Table.HeaderCell>
            <Table.HeaderCell>Domain requested</Table.HeaderCell>
            <Table.HeaderCell>Origin ip:port</Table.HeaderCell>
            <Table.HeaderCell>Time</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {input_data.map(log => (
            <Table.Row>
              <Table.Cell>{log.resolved_to}</Table.Cell>
              <Table.Cell>{log.domain}</Table.Cell>
              <Table.Cell>
                {log.origin_ip}:{log.port}
              </Table.Cell>
              <Table.Cell>{log.created_date}</Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    );
  }
  render() {
    return (
      <div>
        <Grid textAlign="center" style={{ height: "25vh" }}>
          <Grid.Row>
            <Grid.Column width={3}>
              <Dropdown
                placeholder="Select dns bin"
                search
                selection
                onChange={this.onChange}
                options={this.state.bins}
              />
              <br/>
              <br/>
              {this.state.selected !== "" &&
              (<div>
                <Segment.Group >
                  <Segment
                  textAlign='left'
                  inverted
                  primary
                  >
                    Rebinding flow:
                  </Segment>
                {this.state.props.map(i => (
                  <Segment
                    textAlign='left'
                    secondary
                    inverted
                  >
                  {
                    (i.ip.length > 16) && (
                    <Popup
                    content={i.ip}
                    trigger={<div>
                    { i.type===undefined ? "A":i.type} "{i.ip.slice(0, 5)+'...'+i.ip.slice(-5)}" <b>{i.repeat}</b> time{(i.repeat==1) ? '':'s'}
                    </div>}
                    />
                  )
                  }
                  {
                    (i.ip.length <= 16) &&
                    (
                      <div>
                      { i.type===undefined ? "A":i.type} "{i.ip}" <b>{i.repeat}</b> time{(i.repeat==1) ? '':'s'}
                      </div>
                    )
                  }
                  </Segment>
                ))}

                </Segment.Group>
                <Segment
                textAlign='left'
                tertiary
                inverted
                >
                <b>{this.state.total_entries}</b> DNS queries recieved
                </Segment>
                <Button.Group vertical>
                <CopyToClipboard
                  text={this.state.selected+".gel0.space"}
                  onCopy={() => this.setState({copied: true})}
                >
                  <Button
                    icon='copy outline'
                    labelPosition='left'
                    content='Copy domain name'
                    color='olive'
                    inverted
                  />
                </CopyToClipboard>
                <Popup
                  inverted
                  header='Are you sure?'
                  on='click'
                  trigger={
                      <Button
                      width={2}
                      icon='trash alternate'
                      labelPosition='left'
                      color='red'
                      content='Delete this bin'
                      inverted
                      />
                  }
                  content={
                    <Button
                      width={2}
                      onClick={this.deleteUUID}
                      icon='exclamation'
                      labelPosition='left'
                      color='red'
                      content={'I\'m sure, just delete it'}
                    />
                  }
                />
                </Button.Group>

                    </div>)
            }
            </Grid.Column>
            <Grid.Column
              width={10}
            >
              {this.state.selected === "" && (
                <Header
                  size="huge"
                  icon
                  inverted
                  textAlign="center"
                >
                  <Icon
                    name="shuffle"
                    inverted
                    circular
                  />
                  <Header.Content>Select your DNS bin!</Header.Content>

                </Header>
              )}
              {this.state.selected !== "" && this.logsTable(this.state.logs)}
              {this.state.selected !== "" &&
              (<Grid
                columns={1}
               >
                <Grid.Column>
                  <Pagination
                    inverted
                    activePage={this.state.curr_page}
                    boundaryRange={1}
                    onPageChange={this.handlePaginationChange}
                    size='small'
                    siblingRange={1}
                    totalPages={this.state.total_pages}
                    firstItem={null}
                    lastItem={null}
                    prevItem={(this.state.curr_page!==1) ? undefined : null}
                    nextItem={(this.state.curr_page!==this.state.total_pages) ? undefined : null}
                  />
                </Grid.Column>
              </Grid>)}

            </Grid.Column>
            {this.state.selected !== "" &&
            (<Grid.Column width={1}>
              <Button
                circular
                inverted
                icon="redo"
                onClick={this.handleReload}
              />
            </Grid.Column>)}
          </Grid.Row>
        </Grid>
      </div>
    );
  }
}

export default MyBins;

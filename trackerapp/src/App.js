import React, {Component} from "react";
import Plot from 'react-plotly.js';
import Select from 'react-select';
import graphs from "./graphs"


const keyToLabel = (key) => {
  const [start, end, who] = key.split('_')
  return `${who.toUpperCase()} - ${start}`;
}
const keys = Object.keys(graphs);
const options = keys.map(key => {return {value: key, label: keyToLabel(key)}})

class App extends Component {
  state = {option: keys[0]}

  onChange = (
    inputValue,
    {action, prevInputValue}
  ) => {
    switch (action) {
      case 'select-option':
        console.log(this.state)
        this.setState({option: inputValue.value});
    }
  };


  render() {
    const {option} = this.state;
    console.log(option, options)
    const graph = graphs[option]
    return (
      <div>
        <>
          <Select
            className="basic-single"
            classNamePrefix="select"
            defaultValue={options[options.length - 1]}
            isClearable
            onChange={this.onChange}
            name="color"
            options={options}
          />

          <div
            style={{
              color: 'hsl(0, 0%, 40%)',
              display: 'inline-block',
              fontSize: 12,
              fontStyle: 'italic',
              marginTop: '1em',
            }}
          >
          </div>
        </>
        <Plot {...graph} />
      </div >
    );
  }
}

export default App;

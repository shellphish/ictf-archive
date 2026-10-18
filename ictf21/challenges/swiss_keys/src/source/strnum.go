package main

import (
	"encoding/json"
	"strconv"
)

type strnum string

func (self *strnum) UnmarshalJSON(data []byte) error {
	var stmp string
  var itmp int

  err1 := json.Unmarshal(data, &itmp)
  if err1 == nil {
    *self = strnum(strconv.Itoa(itmp))
  	return nil
  }

  err2 := json.Unmarshal(data, &stmp)
  if err2 == nil {
  	*self = strnum(stmp)
  	return nil
  }

  return err1
}
